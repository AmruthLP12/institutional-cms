import pytest
from django.core.management import call_command
from django.test import Client, RequestFactory
from wagtail.models import Site

from apps.content.models import ContactPage
from apps.core.context_processors import site_context
from apps.home.models import HomePage
from apps.site_settings.models import InstitutionSettings, SiteSettings


@pytest.fixture
def seeded_site(db, home_page):
    """Seed full CMS content including settings."""
    call_command("seed_cms", demo=True, legal=True, navigation=True)
    site = Site.objects.get(is_default_site=True)
    return site


@pytest.mark.django_db
class TestInstitutionSettings:
    def test_settings_alias_and_fields(self, seeded_site):
        """Verify InstitutionSettings is an alias for SiteSettings with all required fields."""
        assert InstitutionSettings is SiteSettings

        settings = SiteSettings.for_site(seeded_site)
        assert settings.institution_name == "Nakashara"
        assert settings.institution_short_name == "NKSR"
        assert settings.building_or_campus == "Administrative Complex, Block A"
        assert settings.address_line_1 == "Institutional Enclave, Campus Road"
        assert settings.city == "Knowledge City"
        assert settings.state == "Karnataka"
        assert settings.postal_code == "560001"
        assert settings.country == "India"
        assert settings.phone_primary == "+91 80 2345 6789"
        assert settings.phone_toll_free == "1800 123 4567"
        assert settings.email_general == "inquiry@nakashara.example.org"
        assert settings.office_hours == "Monday – Friday: 08:30 AM – 05:30 PM IST"
        assert settings.directions_info is not None

    def test_address_helper_properties(self, seeded_site):
        """Verify address formatting and line parsing helper properties."""
        settings = SiteSettings.for_site(seeded_site)
        assert settings.has_address is True
        assert len(settings.address_lines) >= 3
        assert "Institutional Enclave, Campus Road" in settings.formatted_address
        assert "Knowledge City" in settings.formatted_address
        assert "560001" in settings.formatted_address

    def test_social_links_helper_properties(self, seeded_site):
        """Verify social links list property only includes non-empty URLs."""
        settings = SiteSettings.for_site(seeded_site)
        assert settings.has_social_links is True
        links = settings.social_links_list
        assert any(link["platform"] == "twitter" for link in links)
        assert any(link["platform"] == "linkedin" for link in links)
        assert any(link["platform"] == "youtube" for link in links)
        # Verify empty platforms are omitted
        assert not any(link["platform"] == "facebook" for link in links)

    def test_empty_field_omission_safety(self, seeded_site):
        """Verify that when optional fields are empty, helpers return sensible empty values without errors."""
        settings = SiteSettings.for_site(seeded_site)
        settings.building_or_campus = ""
        settings.address_line_1 = ""
        settings.address_line_2 = ""
        settings.city = ""
        settings.state = ""
        settings.postal_code = ""
        settings.country = ""
        settings.phone_primary = ""
        settings.phone_secondary = ""
        settings.phone_toll_free = ""
        settings.fax_number = ""
        settings.email_general = ""
        settings.email_admissions = ""
        settings.email_media = ""
        settings.email_reception = ""
        settings.email_accessibility = ""
        settings.office_hours = ""
        settings.directions_info = ""
        settings.directions_url = ""
        settings.twitter_url = ""
        settings.linkedin_url = ""
        settings.youtube_url = ""
        settings.facebook_url = ""
        settings.instagram_url = ""
        settings.save()

        assert settings.has_address is False
        assert settings.address_lines == []
        assert settings.formatted_address == ""
        assert settings.has_contact_info is False
        assert settings.has_social_links is False
        assert settings.social_links_list == []

    def test_context_processor_injection(self, rf: RequestFactory, seeded_site):
        """Verify context processor injects both site_settings and institution_settings."""
        request = rf.get("/")
        request.site = seeded_site
        context = site_context(request)
        assert "site_settings" in context
        assert "institution_settings" in context
        assert context["site_settings"] == context["institution_settings"]
        assert context["site_settings"].institution_name == "Nakashara"

    def test_footer_rendering_with_site_settings(self, client: Client, seeded_site):
        """Verify footer renders institutional branding, address, phones, and social links."""
        resp = client.get("/")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        assert "Nakashara" in content
        assert "NKSR" in content
        assert "+91 80 2345 6789" in content
        assert "inquiry@nakashara.example.org" in content
        assert "Knowledge City" in content
        assert "https://twitter.com/nakashara" in content

    def test_contact_page_centralized_details(self, client: Client, seeded_site):
        """Verify contact page sidebar renders centralized address and contact details."""
        contact_page = ContactPage.objects.filter(slug="contact").first()
        assert contact_page is not None

        resp = client.get(contact_page.url)
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        assert "Official Institutional Office" in content
        assert "+91 80 2345 6789" in content
        assert "inquiry@nakashara.example.org" in content
        assert "Monday – Friday" in content
        assert "Knowledge Park Metro" in content

    def test_multisite_settings_isolation(self, home_page):
        """Verify multi-site support allows independent settings per Wagtail Site."""
        site1 = Site.objects.get(is_default_site=True)
        settings_site1 = SiteSettings.for_site(site1)
        settings_site1.institution_name = "Site Alpha"
        settings_site1.phone_primary = "+1 555 0001"
        settings_site1.save()

        # Create second home page and site
        home_page2 = HomePage(
            title="Home Beta",
            slug="home-beta",
            hero_headline="Advancing Research Beta",
        )
        home_page.get_parent().add_child(instance=home_page2)
        home_page2.save_revision().publish()

        site2 = Site.objects.create(
            hostname="beta.example.org",
            port=80,
            root_page=home_page2,
            is_default_site=False,
            site_name="Site Beta",
        )

        settings_site2 = SiteSettings.for_site(site2)
        settings_site2.institution_name = "Site Beta Academy"
        settings_site2.phone_primary = "+1 555 0002"
        settings_site2.save()

        assert SiteSettings.for_site(site1).institution_name == "Site Alpha"
        assert SiteSettings.for_site(site1).phone_primary == "+1 555 0001"
        assert SiteSettings.for_site(site2).institution_name == "Site Beta Academy"
        assert SiteSettings.for_site(site2).phone_primary == "+1 555 0002"
