import pytest
from django.core.management import call_command
from django.test import Client
from wagtail.models import Site

from apps.content.models import ContactPage
from apps.events.models import EventIndexPage
from apps.home.models import HomePage, QuickLinkItem
from apps.news.models import NewsIndexPage
from apps.people.models import PersonIndexPage
from apps.site_settings.models import SiteSettings


@pytest.fixture
def seeded_site(db, home_page):
    """Seed full CMS content for test environment."""
    call_command("seed_cms", demo=True, legal=True, navigation=True)
    site = Site.objects.get(is_default_site=True)
    return site


@pytest.mark.django_db
class TestHtmxAndTheme:
    def test_news_index_htmx_partial(self, client: Client, seeded_site):
        news_idx = NewsIndexPage.objects.filter(slug="news").first()
        assert news_idx is not None

        # Regular request returns full page with header & footer
        resp = client.get(news_idx.url)
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.content
        assert b"<header" in resp.content

        # HTMX request returns only partial grid without full document shell
        htmx_resp = client.get(news_idx.url, HTTP_HX_REQUEST="true")
        assert htmx_resp.status_code == 200
        assert b"<!DOCTYPE html>" not in htmx_resp.content

    def test_events_index_htmx_partial(self, client: Client, seeded_site):
        event_idx = EventIndexPage.objects.filter(slug="events").first()
        assert event_idx is not None

        # Regular request
        resp = client.get(event_idx.url)
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.content

        # HTMX request
        htmx_resp = client.get(f"{event_idx.url}?tab=upcoming", HTTP_HX_REQUEST="true")
        assert htmx_resp.status_code == 200
        assert b"<!DOCTYPE html>" not in htmx_resp.content

    def test_people_index_htmx_partial(self, client: Client, seeded_site):
        peo_idx = PersonIndexPage.objects.filter(slug="people").first()
        assert peo_idx is not None

        # Regular request
        resp = client.get(peo_idx.url)
        assert resp.status_code == 200
        assert b"<!DOCTYPE html>" in resp.content

        # HTMX request
        htmx_resp = client.get(peo_idx.url, HTTP_HX_REQUEST="true")
        assert htmx_resp.status_code == 200
        assert b"<!DOCTYPE html>" not in htmx_resp.content

    def test_contact_page_render_and_submit(self, client: Client, seeded_site):
        contact_page = ContactPage.objects.filter(slug="contact").first()
        assert contact_page is not None

        resp = client.get(contact_page.url)
        assert resp.status_code == 200
        assert b"Contact Us" in resp.content
        assert b"Send an Inquiry" in resp.content

        # Submit form
        post_data = {
            "full_name": "Test Visitor",
            "email_address": "visitor@example.org",
            "subject_department": "Admissions",
            "message": "Hello Nakashara team",
        }
        submit_resp = client.post(contact_page.url, post_data)
        assert submit_resp.status_code == 200
        assert b"Inquiry Received" in submit_resp.content

    def test_site_settings_theme_selection(self, client: Client, seeded_site):
        settings = SiteSettings.for_site(seeded_site)
        settings.theme = "emerald"
        settings.save()

        resp = client.get(seeded_site.root_page.url)
        assert resp.status_code == 200
        assert b'data-theme="emerald"' in resp.content

    def test_quick_links_internal_pages(self, seeded_site):
        home = HomePage.objects.first()
        assert home is not None
        quick_links = QuickLinkItem.objects.filter(page=home)
        assert quick_links.count() > 0
        for link in quick_links:
            # Internal links must have link_page set
            assert link.link_page is not None
            assert link.get_url().startswith("/")
