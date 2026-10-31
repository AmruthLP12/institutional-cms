"""
Test Suite for Institutional Design Themes & Admin-Managed Theme Selection.

Covers:
- Default theme when no setting exists ('academic-blue')
- Each of the five valid theme identifiers
- Invalid theme fallback to 'academic-blue'
- Theme selection through Wagtail Site Settings
- Multi-site theme isolation
- Public templates receiving the correct theme
- Theme selection permissions
- No DaisyUI built-in theme configuration remains
- Existing public pages render correctly after the redesign
"""

from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, RequestFactory
from wagtail.models import Site

from apps.core.context_processors import site_context
from apps.home.models import HomePage
from apps.site_settings.models import SiteSettings
from apps.site_settings.themes import (
    DEFAULT_THEME,
    VALID_THEMES,
    get_theme,
)


@pytest.fixture
def seeded_site(db, home_page):
    """Seed full CMS content for test environment."""
    call_command("seed_cms", demo=True, legal=True, navigation=True)
    site = Site.objects.get(is_default_site=True)
    return site


@pytest.mark.django_db
class TestInstitutionalThemes:
    """Comprehensive test suite for institutional themes."""

    def test_default_theme_when_no_setting_exists(self, client: Client, seeded_site):
        """When settings have empty or default theme, active_theme must be academic-blue."""
        settings = SiteSettings.for_site(seeded_site)
        settings.theme = ""
        settings.save()

        assert settings.active_theme == DEFAULT_THEME
        assert settings.active_theme == "academic-blue"

        resp = client.get(seeded_site.root_page.url)
        assert resp.status_code == 200
        assert b'data-theme="academic-blue"' in resp.content

    def test_all_five_valid_theme_identifiers(self, client: Client, seeded_site):
        """Each of the five institutional themes can be activated and renders correctly."""
        expected_themes = [
            "academic-blue",
            "sage-ivory",
            "slate-steel",
            "burgundy-cream",
            "teal-stone",
        ]
        assert set(expected_themes) == VALID_THEMES

        settings = SiteSettings.for_site(seeded_site)
        for theme_id in expected_themes:
            settings.theme = theme_id
            settings.save()
            settings.refresh_from_db()

            assert settings.active_theme == theme_id
            meta = get_theme(theme_id)
            assert meta["id"] == theme_id
            assert "name" in meta
            assert "colors" in meta
            assert "primary" in meta["colors"]
            assert "surface" in meta["colors"]
            assert "page_bg" in meta["colors"]

            resp = client.get(seeded_site.root_page.url)
            assert resp.status_code == 200
            assert f'data-theme="{theme_id}"'.encode() in resp.content

    def test_invalid_theme_fallback(self, client: Client, seeded_site):
        """Invalid, legacy, or injection theme strings safely fall back to academic-blue."""
        settings = SiteSettings.for_site(seeded_site)

        for invalid_val in [
            "corporate",
            "emerald",
            "nord",
            "cyberpunk",
            "random-theme",
            "<script>alert(1)</script>",
            "'; DROP TABLE users; --",
        ]:
            settings.theme = invalid_val
            settings.save()

            assert settings.active_theme == DEFAULT_THEME
            assert settings.active_theme == "academic-blue"

            resp = client.get(seeded_site.root_page.url)
            assert resp.status_code == 200
            assert b'data-theme="academic-blue"' in resp.content
            # Ensure no unescaped injection or invalid string in data-theme
            assert f'data-theme="{invalid_val}"'.encode() not in resp.content

    def test_site_specific_theme_isolation(self, home_page):
        """Multi-site support allows independent themes per Wagtail Site."""
        site1 = Site.objects.get(is_default_site=True)
        site1.hostname = "localhost"
        site1.port = 80
        site1.save()

        settings_site1 = SiteSettings.for_site(site1)
        settings_site1.theme = "sage-ivory"
        settings_site1.save()

        # Create second home page and site
        home_page2 = HomePage(
            title="Nakashara Technology Campus",
            slug="tech-campus",
            hero_headline="Engineering & Applied Sciences",
        )
        home_page.get_parent().add_child(instance=home_page2)
        home_page2.save_revision().publish()

        site2 = Site.objects.create(
            hostname="testserver",
            port=8080,
            root_page=home_page2,
            is_default_site=False,
            site_name="Technology Campus",
        )

        settings_site2 = SiteSettings.for_site(site2)
        settings_site2.theme = "burgundy-cream"
        settings_site2.save()

        # Verify database isolation
        assert SiteSettings.for_site(site1).active_theme == "sage-ivory"
        assert SiteSettings.for_site(site2).active_theme == "burgundy-cream"

        # Verify context processor per site request
        rf = RequestFactory()

        req1 = rf.get("/", HTTP_HOST="localhost")
        req1.site = site1
        assert site_context(req1)["site_settings"].active_theme == "sage-ivory"

        req2 = rf.get("/", HTTP_HOST="testserver:8080")
        req2.site = site2
        assert site_context(req2)["site_settings"].active_theme == "burgundy-cream"

    def test_public_templates_receive_correct_theme(self, client: Client, seeded_site):
        """All public sections inherit the active theme."""
        settings = SiteSettings.for_site(seeded_site)
        settings.theme = "teal-stone"
        settings.save()

        urls_to_test = [
            "/",
            "/news/",
            "/events/",
            "/people/",
            "/departments/",
            "/research/",
            "/documents/",
            "/policies/",
            "/contact/",
            "/search/?query=research",
        ]

        for url in urls_to_test:
            resp = client.get(url)
            assert resp.status_code == 200, f"Failed at URL {url}"
            assert b'data-theme="teal-stone"' in resp.content, f"data-theme missing on {url}"

    def test_theme_selection_permissions(self, client: Client, seeded_site):
        """Standard non-staff users cannot edit site settings; staff with permission can."""
        User = get_user_model()
        user_plain = User.objects.create_user(username="student_user", password="password123")
        user_admin = User.objects.create_user(
            username="theme_admin_user",
            password="password123",
            is_staff=True,
            is_superuser=True,
        )

        settings = SiteSettings.for_site(seeded_site)
        admin_url = f"/admin/settings/site_settings/sitesettings/{settings.id}/"

        # Unauthenticated / plain user cannot access Wagtail admin settings
        client.force_login(user_plain)
        admin_resp = client.get(admin_url)
        # Redirected or 403
        assert admin_resp.status_code in [302, 403]

        # Authorized admin can access settings
        client.force_login(user_admin)
        admin_resp = client.get("/admin/settings/site_settings/sitesettings/", follow=True)
        assert admin_resp.status_code == 200
        assert b"Academic Blue" in admin_resp.content
        assert b"Sage &amp; Ivory" in admin_resp.content or b"Sage & Ivory" in admin_resp.content
        assert b"Slate &amp; Steel" in admin_resp.content or b"Slate & Steel" in admin_resp.content
        assert b"Burgundy &amp; Cream" in admin_resp.content or b"Burgundy & Cream" in admin_resp.content
        assert b"Teal &amp; Stone" in admin_resp.content or b"Teal & Stone" in admin_resp.content

    def test_no_daisyui_builtin_themes_configuration(self):
        """Verify DaisyUI theme system configuration and built-in palettes are completely removed."""
        base_dir = Path(__file__).resolve().parent.parent

        # 1. Inspect styles.css source
        styles_path = base_dir / "theme" / "static_src" / "src" / "styles.css"
        assert styles_path.exists()
        styles_content = styles_path.read_text(encoding="utf-8")

        # Must not contain themes: all
        assert "themes: all" not in styles_content
        # Must disable DaisyUI themes
        assert "themes: false" in styles_content
        # Must not contain old corporate or built-in DaisyUI theme overrides
        assert '[data-theme="corporate"]' not in styles_content
        assert '[data-theme="emerald"]' not in styles_content
        assert '[data-theme="nord"]' not in styles_content
        assert '[data-theme="autumn"]' not in styles_content
        assert '[data-theme="luxury"]' not in styles_content

        # Must contain all five institutional theme token definitions
        for theme_id in VALID_THEMES:
            assert f'[data-theme="{theme_id}"]' in styles_content

        # 2. Inspect compiled CSS distribution
        dist_css_path = base_dir / "theme" / "static" / "css" / "dist" / "styles.css"
        assert dist_css_path.exists()
        dist_content = dist_css_path.read_text(encoding="utf-8")

        # Compiled CSS must define the 5 institutional themes
        for theme_id in VALID_THEMES:
            assert f'data-theme="{theme_id}"' in dist_content or f'data-theme={theme_id}' in dist_content

        # Compiled CSS must NOT contain unconfigured built-in DaisyUI themes
        for unwanted_theme in ["corporate", "cyberpunk", "dracula", "synthwave", "valentine", "halloween", "cupcake"]:
            assert f'data-theme="{unwanted_theme}"' not in dist_content
            assert f'data-theme={unwanted_theme}' not in dist_content

    def test_clean_method_defaults_invalid_theme(self):
        """SiteSettings.clean() forces invalid theme values back to DEFAULT_THEME."""
        setting = SiteSettings(theme="unknown-theme")
        setting.clean()
        assert setting.theme == DEFAULT_THEME
