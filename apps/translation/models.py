"""
apps/translation/models.py — Multilingual settings, language configuration, and translation metadata.
"""

import hashlib
import json
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Locale, Orderable, Page
from wagtail.snippets.models import register_snippet


class TranslationWorkflowStatus(models.TextChoices):
    DRAFT = "draft", "Draft / Unreviewed"
    IN_REVIEW = "in_review", "In Review"
    APPROVED = "approved", "Approved & Published"
    OUTDATED = "outdated", "Source Modified (Outdated)"


@register_setting
class LanguageSettings(BaseSiteSetting, ClusterableModel):
    """
    Site settings to configure active languages and default translation workflows.
    """

    default_translation_provider = models.CharField(
        max_length=50,
        choices=[
            ("mock", "Mock Provider (Offline / Testing)"),
            ("google", "Google Cloud Translation"),
        ],
        default="mock",
        help_text="Primary translation provider for automatic translation requests.",
    )
    auto_create_draft_translations = models.BooleanField(
        default=True,
        help_text="When saving a page in the default language, automatically prepare translation drafts.",
    )
    require_review_before_publishing = models.BooleanField(
        default=True,
        help_text="Enforce editorial review for machine translations before allowing live publication.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("default_translation_provider"),
                FieldPanel("auto_create_draft_translations"),
                FieldPanel("require_review_before_publishing"),
            ],
            heading="Translation Engine & Automation",
        ),
        InlinePanel("managed_languages", label="Configured Languages", heading="Language Registry"),
    ]

    class Meta:
        verbose_name = "Language & Translation Settings"


class ManagedLanguage(Orderable):
    """
    Languages active on the public site and within Wagtail CMS.
    """

    setting = ParentalKey(
        LanguageSettings,
        on_delete=models.CASCADE,
        related_name="managed_languages",
    )
    locale = models.ForeignKey(
        Locale,
        on_delete=models.CASCADE,
        related_name="managed_configurations",
        help_text="Wagtail Locale record for this language.",
    )
    native_name = models.CharField(
        max_length=100,
        help_text="Name displayed in language switcher (e.g., 'ಕನ್ನಡ', 'हिन्दी', 'English').",
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Mark this language as the institutional primary language.",
    )
    is_enabled = models.BooleanField(
        default=True,
        help_text="Enable on public site language switchers.",
    )
    is_rtl = models.BooleanField(
        default=False,
        help_text="Check if this language is written Right-to-Left (e.g. Arabic, Urdu).",
    )

    panels = [
        FieldPanel("locale"),
        FieldPanel("native_name"),
        FieldPanel("is_default"),
        FieldPanel("is_enabled"),
        FieldPanel("is_rtl"),
    ]

    def __str__(self):
        return f"{self.native_name} ({self.locale.language_code})"


@register_snippet
class TranslationRecord(models.Model):
    """
    Metadata recording translation status, provider, and source freshness hash for a translated page.
    """

    source_page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="translation_targets",
        help_text="Original source page from which translation was generated.",
    )
    translated_page = models.OneToOneField(
        Page,
        on_delete=models.CASCADE,
        related_name="translation_record",
        help_text="Translated counterpart page.",
    )
    status = models.CharField(
        max_length=30,
        choices=TranslationWorkflowStatus.choices,
        default=TranslationWorkflowStatus.DRAFT,
        db_index=True,
    )
    provider_used = models.CharField(
        max_length=50,
        default="manual",
        help_text="Provider used ('manual', 'mock', 'google').",
    )
    source_content_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash of the source page title, intro, and body when translation occurred.",
    )
    last_translated_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp of the most recent translation pass.",
    )
    translator_notes = models.TextField(
        blank=True,
        help_text="Reviewer or translator notes.",
    )

    panels = [
        FieldPanel("status"),
        FieldPanel("provider_used"),
        FieldPanel("translator_notes"),
    ]

    def is_outdated(self) -> bool:
        """Check if source content hash differs from current source content."""
        if not self.source_page or not self.source_content_hash:
            return False
        current_hash = self.calculate_content_hash(self.source_page.specific)
        return current_hash != self.source_content_hash

    @staticmethod
    def calculate_content_hash(page: Page) -> str:
        """Calculate a deterministic hash of translatable content."""
        if hasattr(page, "specific"):
            page = page.specific
        elements = [str(page.title)]
        if hasattr(page, "meta_description") and page.meta_description:
            elements.append(str(page.meta_description))
        if hasattr(page, "intro") and page.intro:
            elements.append(str(page.intro))
        if hasattr(page, "body") and page.body:
            try:
                elements.append(json.dumps(page.body.raw_data, sort_keys=True))
            except Exception:
                elements.append(str(page.body))
        content_bytes = "|".join(elements).encode("utf-8")
        return hashlib.sha256(content_bytes).hexdigest()

    def __str__(self):
        return f"Translation: {self.translated_page.title} ({self.translated_page.locale.language_code}) - {self.get_status_display()}"
