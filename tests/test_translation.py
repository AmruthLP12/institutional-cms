"""
Tests for Multilingual Content and Translation Management.
"""

import pytest
from django.test import Client
from django.utils import timezone
from wagtail.models import Locale, Page, Site

from apps.home.models import HomePage
from apps.translation.engine import TranslationEngine
from apps.translation.models import (
    LanguageSettings,
    ManagedLanguage,
    TranslationRecord,
    TranslationWorkflowStatus,
)
from apps.translation.providers import get_translation_provider
from apps.translation.providers.mock import MockTranslationProvider


@pytest.mark.django_db
class TestMultilingualSystem:
    def test_configured_locales_exist(self):
        """Verify en, kn, and hi locales can be registered."""
        Locale.objects.get_or_create(language_code="en")
        Locale.objects.get_or_create(language_code="kn")
        Locale.objects.get_or_create(language_code="hi")
        locales = list(Locale.objects.values_list("language_code", flat=True))
        assert "en" in locales
        assert "kn" in locales
        assert "hi" in locales

    def test_mock_translation_provider(self):
        """Verify MockTranslationProvider dictionary matches and fallbacks."""
        provider = MockTranslationProvider()
        # Exact dictionary lookup
        assert provider.translate_text("Nakashara", "kn") == "ನಕಾಶರ"
        assert provider.translate_text("Nakashara", "hi") == "नकाशरा"
        assert provider.translate_text("Contact", "kn") == "ಸಂಪರ್ಕಿಸಿ"

        # General text prefixing
        translated = provider.translate_text("Sample Title", "kn")
        assert translated == "[ಕನ್ನಡ] Sample Title"

        # HTML wrapping
        html_trans = provider.translate_text("<p>Hello</p>", "hi", is_html=True)
        assert "[हिन्दी]" in html_trans

    def test_translation_engine_creates_draft_translation(self, home_page):
        """Verify TranslationEngine clones page and marks as draft."""
        kn_locale, _ = Locale.objects.get_or_create(language_code="kn")
        engine = TranslationEngine(provider=MockTranslationProvider())
        translated_home = engine.translate_page(
            home_page, kn_locale, save_draft=True
        )

        assert translated_home.locale == kn_locale
        assert translated_home.title == "ನಕಾಶರ"
        assert translated_home.live is False  # Must be saved as draft
        assert translated_home.has_unpublished_changes is True

        # Check translation record
        record = TranslationRecord.objects.get(translated_page=translated_home)
        assert record.source_page.id == home_page.id
        assert record.status == TranslationWorkflowStatus.DRAFT
        assert record.provider_used == "mock"

    def test_outdated_freshness_detection(self, home_page):
        """Verify modifying the source page marks translation as outdated."""
        hi_locale, _ = Locale.objects.get_or_create(language_code="hi")
        engine = TranslationEngine(provider=MockTranslationProvider())
        translated_home = engine.translate_page(
            home_page, hi_locale, save_draft=True
        )
        record = TranslationRecord.objects.get(translated_page=translated_home)

        # Before modifying source
        assert record.is_outdated() is False

        # Modify source page title
        original_title = home_page.title
        home_page.title = "Nakashara Institute of Advanced Science"
        home_page.save()

        # Reload record to clear any cached source_page instance
        record = TranslationRecord.objects.get(id=record.id)
        # Check freshness
        assert record.is_outdated() is True

        # Restore title
        home_page.title = original_title
        home_page.save()

    def test_language_switcher_rendering(self, client, home_page):
        """Verify language switcher exists on the public page with available options."""
        response = client.get("/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")

        # Utility bar language switcher should be present
        assert "Language" in content or "EN" in content or "ಕನ್ನಡ" in content
        # hreflang tags
        assert 'hreflang="en"' in content

    def test_hreflang_urls_on_base_page(self, home_page):
        """Verify get_hreflang_urls outputs canonical urls for active translations."""
        urls = home_page.get_hreflang_urls()
        assert "en" in urls
        assert len(urls) >= 1
