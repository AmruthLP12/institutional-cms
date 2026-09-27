"""
Site Settings — global CMS configuration, navigation, alert banners.
"""

from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.models import Orderable, Page
from wagtail.snippets.models import register_snippet


@register_setting
class SiteSettings(BaseSiteSetting):
    """
    Global site configuration editable via Wagtail admin Settings panel.
    """

    # Identity
    institution_name = models.CharField(
        max_length=200,
        default="Nakashara",
        help_text="Full institution name.",
    )
    institution_short_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Abbreviated name (e.g. NKSR).",
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        help_text="Institutional tagline shown in header/footer.",
    )

    # Appearance & Theme
    THEME_CHOICES = [
        ("corporate", "Corporate (Clean Modern Blue & Slate)"),
        ("emerald", "Emerald (Academic Deep Green & Mint)"),
        ("nord", "Nord (Modern Arctic Slate & Frost)"),
        ("winter", "Winter (Crisp Professional Cyan & Ice)"),
        ("business", "Business (High-Contrast Corporate Dark)"),
        ("night", "Night (Deep Modern Dark)"),
        ("autumn", "Autumn (Warm Rust, Bronze & Cream)"),
        ("luxury", "Luxury (Dark Gold & Deep Obsidian)"),
        ("light", "Light (Default Clean Bright)"),
    ]
    theme = models.CharField(
        max_length=50,
        choices=THEME_CHOICES,
        default="corporate",
        help_text="Color palette and theme for the entire website.",
    )
    custom_primary_color = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional hex color to override primary brand color (e.g. #1E40AF or #047857).",
    )
    custom_accent_color = models.CharField(
        max_length=30,
        blank=True,
        help_text="Optional hex color to override secondary/accent color (e.g. #D97706 or #E11D48).",
    )

    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Institution logo (SVG or PNG, transparent background).",
    )
    logo_alt_text = models.CharField(
        max_length=200,
        blank=True,
        default="Nakashara logo",
        help_text="Alt text for the logo image.",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Favicon (32×32 or 64×64 px, ICO/PNG).",
    )

    # Contact
    address_line_1 = models.CharField(max_length=300, blank=True)
    address_line_2 = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default="India")
    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email_general = models.EmailField(blank=True)
    email_admissions = models.EmailField(blank=True)

    # Social links
    twitter_url = models.URLField(blank=True, verbose_name="Twitter/X URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")

    # Footer
    footer_copyright_text = models.CharField(
        max_length=400,
        blank=True,
        help_text="Copyright line in footer.",
    )
    footer_note = models.TextField(
        blank=True,
        help_text="Optional additional note in footer.",
    )

    # Analytics — optional, institution-specific
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Google Analytics GA4 Measurement ID (e.g. G-XXXXXXXXXX). Leave blank to disable.",
    )

    # Admin panels
    identity_panels = [
        MultiFieldPanel(
            [
                FieldPanel("institution_name"),
                FieldPanel("institution_short_name"),
                FieldPanel("tagline"),
                FieldPanel("logo"),
                FieldPanel("logo_alt_text"),
                FieldPanel("favicon"),
            ],
            heading="Identity",
        ),
    ]

    contact_panels = [
        MultiFieldPanel(
            [
                FieldPanel("address_line_1"),
                FieldPanel("address_line_2"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("postal_code"),
                FieldPanel("country"),
                FieldPanel("phone_primary"),
                FieldPanel("phone_secondary"),
                FieldPanel("email_general"),
                FieldPanel("email_admissions"),
            ],
            heading="Contact information",
        ),
    ]

    social_panels = [
        MultiFieldPanel(
            [
                FieldPanel("twitter_url"),
                FieldPanel("linkedin_url"),
                FieldPanel("youtube_url"),
                FieldPanel("facebook_url"),
                FieldPanel("instagram_url"),
            ],
            heading="Social media",
        ),
    ]

    footer_panels = [
        MultiFieldPanel(
            [
                FieldPanel("footer_copyright_text"),
                FieldPanel("footer_note"),
            ],
            heading="Footer content",
        ),
    ]

    analytics_panels = [
        FieldPanel("google_analytics_id"),
    ]

    theme_panels = [
        MultiFieldPanel(
            [
                FieldPanel("theme"),
                FieldPanel("custom_primary_color"),
                FieldPanel("custom_accent_color"),
            ],
            heading="Theme & Appearance",
        ),
    ]

    panels = (
        identity_panels
        + theme_panels
        + contact_panels
        + social_panels
        + footer_panels
        + analytics_panels
    )

    class Meta:
        verbose_name = "Site Settings"


class NavMenuItem(ClusterableModel, Orderable):
    """
    Navigation menu item — can be a page link or external URL,
    with optional children for dropdown menus.
    """

    parent = ParentalKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )
    label = models.CharField(
        max_length=100,
        help_text="Navigation label shown to users.",
    )
    page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Link to a Wagtail page.",
    )
    external_url = models.URLField(
        blank=True,
        help_text="External URL (used if no page selected).",
    )
    open_in_new_tab = models.BooleanField(
        default=False,
        help_text="Open link in a new browser tab.",
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_visible = models.BooleanField(
        default=True, help_text="Show this item in the navigation."
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("page"),
        FieldPanel("external_url"),
        FieldPanel("open_in_new_tab"),
        FieldPanel("order"),
        FieldPanel("is_visible"),
    ]

    def get_url(self) -> str:
        """Return the URL for this nav item."""
        if self.page:
            return self.page.url
        return self.external_url or "#"

    class Meta:
        verbose_name = "Navigation menu item"
        verbose_name_plural = "Navigation menu items"
        ordering = ["order"]


@register_snippet
class AlertBanner(models.Model):
    """
    Site-wide alert banner shown at the top of every page.
    Only one banner should be active at a time.
    """

    BANNER_TYPES = [
        ("info", "Information"),
        ("warning", "Warning"),
        ("critical", "Critical / Emergency"),
    ]

    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default="info")
    title = models.CharField(max_length=200, blank=True)
    message = models.TextField(
        help_text="Short message displayed in the banner.",
    )
    link_text = models.CharField(
        max_length=100, blank=True, help_text="Optional link label."
    )
    link_url = models.URLField(blank=True, help_text="Optional link URL.")
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("banner_type"),
        FieldPanel("title"),
        FieldPanel("message"),
        FieldPanel("link_text"),
        FieldPanel("link_url"),
        FieldPanel("is_active"),
    ]

    def __str__(self):
        return f"[{self.banner_type.upper()}] {self.title or self.message[:60]}"

    class Meta:
        verbose_name = "Alert banner"
        verbose_name_plural = "Alert banners"
        ordering = ["-created_at"]


@register_snippet
class FooterLinkGroup(ClusterableModel):
    """Group of links shown in the footer (e.g. 'Quick Links', 'Policies')."""

    title = models.CharField(max_length=100)
    order = models.PositiveSmallIntegerField(default=0)

    panels = [
        FieldPanel("title"),
        FieldPanel("order"),
        InlinePanel("links", label="Footer links"),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Footer link group"
        verbose_name_plural = "Footer link groups"
        ordering = ["order"]


class FooterLink(Orderable):
    """Single link within a footer group."""

    group = ParentalKey(FooterLinkGroup, on_delete=models.CASCADE, related_name="links")
    label = models.CharField(max_length=100)
    page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    external_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    panels = [
        FieldPanel("label"),
        FieldPanel("page"),
        FieldPanel("external_url"),
        FieldPanel("order"),
    ]

    def get_url(self) -> str:
        if self.page:
            return self.page.url
        return self.external_url or "#"

    class Meta:
        ordering = ["order"]
