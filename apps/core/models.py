"""
Core app — base models, reusable blocks, shared utilities.
"""

from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page
from wagtail.search import index


class BasePage(Page):
    """
    Abstract base page with SEO and meta fields.
    All institutional page types inherit from this.
    """

    meta_description = models.CharField(
        max_length=320,
        blank=True,
        help_text="Brief description for search engines (150–320 characters).",
    )
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Social sharing image (1200×630 px recommended).",
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Override canonical URL if this page has a preferred URL.",
    )
    robots_noindex = models.BooleanField(
        default=False,
        help_text="Prevent search engines from indexing this page.",
    )

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("meta_description"),
                FieldPanel("og_image"),
                FieldPanel("canonical_url"),
                FieldPanel("robots_noindex"),
            ],
            heading="SEO and sharing",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("meta_description"),
    ]

    def get_meta_description(self) -> str:
        """Return meta description or a sensible fallback."""
        if self.meta_description:
            return self.meta_description
        if hasattr(self, "intro") and self.intro:
            text = self.intro
            if hasattr(text, "source"):
                text = text.source  # RichTextField
            return str(text)[:320]
        return ""

    def get_canonical_url(self, request=None) -> str:
        """Return canonical URL, preferring explicit override."""
        if self.canonical_url:
            return self.canonical_url
        if request:
            return request.build_absolute_uri(self.url)
        return self.full_url or ""

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract model with created_at and updated_at timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
