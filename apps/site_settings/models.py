"""
Site Settings — global CMS configuration, navigation, alert banners.
"""

from django.core.validators import RegexValidator
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

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r"^#(?:[0-9a-fA-F]{3}){1,2}$",
    message="Enter a valid 3- or 6-digit hex color code starting with # (e.g. #24466B).",
)


@register_setting
class SiteSettings(BaseSiteSetting):
    """
    Global site and institutional configuration editable via Wagtail admin Settings panel.
    """

    # Identity
    institution_name = models.CharField(
        max_length=200,
        default="Nakashara",
        help_text="Full official institution name.",
    )
    institution_short_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Abbreviated name or acronym (e.g. NKSR).",
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        help_text="Institutional tagline shown in header/footer.",
    )
    footer_description = models.TextField(
        blank=True,
        help_text="Short institutional description shown in footer.",
    )

    # Appearance & Theme
    THEME_CHOICES = [
        ("corporate", "Nakashara Oxford (Institutional Navy, Sage & Gold)"),
        ("emerald", "Emerald (Academic Forest Green & Mint)"),
        ("nord", "Nord (Modern Arctic Slate & Frost)"),
        ("winter", "Winter (Crisp Professional Cyan & Ice)"),
        ("autumn", "Autumn (Warm Terracotta, Bronze & Cream)"),
        ("luxury", "Luxury (Distinguished Obsidian & Burnished Gold)"),
        ("business", "Business (High-Contrast Corporate Dark)"),
        ("night", "Night (Deep Modern Academic Dark)"),
        ("light", "Light (Clean Editorial Minimalist)"),
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
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Optional hex color to override primary brand color (e.g. #24466B).",
    )
    custom_accent_color = models.CharField(
        max_length=30,
        blank=True,
        validators=[HEX_COLOR_VALIDATOR],
        help_text="Optional hex color to override secondary/accent color (e.g. #B58A48).",
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

    # Contact Details
    email_general = models.EmailField(
        blank=True,
        help_text="General institutional inquiry email.",
    )
    email_admissions = models.EmailField(
        blank=True,
        help_text="Admissions & student inquiries email.",
    )
    email_reception = models.EmailField(
        blank=True,
        help_text="Front desk, reception, or helpdesk email.",
    )
    email_accessibility = models.EmailField(
        blank=True,
        help_text="Accessibility officer or compliance contact email.",
    )
    phone_primary = models.CharField(
        max_length=30,
        blank=True,
        help_text="Main institutional switchboard / telephone number.",
    )
    phone_secondary = models.CharField(
        max_length=30,
        blank=True,
        help_text="Alternate telephone number.",
    )
    phone_toll_free = models.CharField(
        max_length=30,
        blank=True,
        help_text="Toll-free or student helpline telephone number.",
    )
    fax_number = models.CharField(
        max_length=30,
        blank=True,
        help_text="Official institutional facsimile number.",
    )

    # Structured Postal Address
    address_line_1 = models.CharField(
        max_length=300,
        blank=True,
        help_text="Primary street address or building number.",
    )
    address_line_2 = models.CharField(
        max_length=300,
        blank=True,
        help_text="Secondary address details (suite, block, floor).",
    )
    building_or_campus = models.CharField(
        max_length=200,
        blank=True,
        help_text="Campus name, locality, or sector.",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City or municipality.",
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State, province, or region.",
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal code or PIN code.",
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        default="India",
        help_text="Country name.",
    )

    # Office Hours & Directions
    office_hours = models.CharField(
        max_length=200,
        blank=True,
        default="Monday – Friday: 9:00 AM – 5:00 PM IST",
        help_text="Standard administrative office hours.",
    )
    directions_info = models.TextField(
        blank=True,
        help_text="Brief visitor guidance, transit routes, or parking details.",
    )
    directions_url = models.URLField(
        blank=True,
        help_text="Official Google Maps or transit directions URL.",
    )

    # Social Links
    twitter_url = models.URLField(blank=True, verbose_name="Twitter/X URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    youtube_url = models.URLField(blank=True, verbose_name="YouTube URL")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook URL")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram URL")

    # Footer & Legal
    footer_copyright_text = models.CharField(
        max_length=400,
        blank=True,
        help_text="Copyright line shown in footer (defaults to current year + institution name).",
    )
    footer_note = models.TextField(
        blank=True,
        help_text="Optional statutory or accreditation note in footer.",
    )

    # Analytics
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Google Analytics GA4 Measurement ID (e.g. G-XXXXXXXXXX). Leave blank to disable.",
    )

    # Admin Panels
    identity_panels = [
        MultiFieldPanel(
            [
                FieldPanel("institution_name"),
                FieldPanel("institution_short_name"),
                FieldPanel("tagline"),
                FieldPanel("footer_description"),
                FieldPanel("logo"),
                FieldPanel("logo_alt_text"),
                FieldPanel("favicon"),
            ],
            heading="Institutional Identity",
        ),
    ]

    contact_panels = [
        MultiFieldPanel(
            [
                FieldPanel("email_general"),
                FieldPanel("email_admissions"),
                FieldPanel("email_reception"),
                FieldPanel("email_accessibility"),
                FieldPanel("phone_primary"),
                FieldPanel("phone_secondary"),
                FieldPanel("phone_toll_free"),
                FieldPanel("fax_number"),
            ],
            heading="General Contact Information",
        ),
    ]

    address_panels = [
        MultiFieldPanel(
            [
                FieldPanel("address_line_1"),
                FieldPanel("address_line_2"),
                FieldPanel("building_or_campus"),
                FieldPanel("city"),
                FieldPanel("state"),
                FieldPanel("postal_code"),
                FieldPanel("country"),
            ],
            heading="Postal Address",
        ),
    ]

    operations_panels = [
        MultiFieldPanel(
            [
                FieldPanel("office_hours"),
                FieldPanel("directions_info"),
                FieldPanel("directions_url"),
            ],
            heading="Office Hours & Directions",
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
            heading="Social Media Links",
        ),
    ]

    footer_panels = [
        MultiFieldPanel(
            [
                FieldPanel("footer_copyright_text"),
                FieldPanel("footer_note"),
            ],
            heading="Footer Content & Legal",
        ),
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

    analytics_panels = [
        FieldPanel("google_analytics_id"),
    ]

    panels = (
        identity_panels
        + contact_panels
        + address_panels
        + operations_panels
        + social_panels
        + footer_panels
        + theme_panels
        + analytics_panels
    )

    # ─── Helper Properties & Formatting Methods ──────────────────────
    @property
    def formatted_address(self) -> str:
        """
        Return a single-line comma-separated address string,
        omitting any empty fields cleanly.
        """
        parts = []
        if self.address_line_1:
            parts.append(self.address_line_1.strip())
        if self.address_line_2:
            parts.append(self.address_line_2.strip())
        if self.building_or_campus:
            parts.append(self.building_or_campus.strip())

        city_state_zip = []
        if self.city:
            city_state_zip.append(self.city.strip())
        if self.state:
            city_state_zip.append(self.state.strip())
        city_state_str = ", ".join(city_state_zip)
        if self.postal_code:
            city_state_str = f"{city_state_str} {self.postal_code.strip()}".strip()
        if city_state_str:
            parts.append(city_state_str)

        if self.country:
            parts.append(self.country.strip())

        return ", ".join(parts)

    @property
    def address_lines(self) -> list[str]:
        """
        Return structured non-empty address lines for multi-line rendering.
        """
        lines = []
        if self.address_line_1:
            lines.append(self.address_line_1.strip())
        if self.address_line_2:
            lines.append(self.address_line_2.strip())
        if self.building_or_campus:
            lines.append(self.building_or_campus.strip())

        city_line_parts = []
        if self.city:
            city_line_parts.append(self.city.strip())
        if self.state:
            city_line_parts.append(self.state.strip())
        city_line = ", ".join(city_line_parts)
        if self.postal_code:
            city_line = f"{city_line} {self.postal_code.strip()}".strip()
        if self.country:
            city_line = f"{city_line}, {self.country.strip()}".strip(", ")
        if city_line:
            lines.append(city_line)

        return lines

    @property
    def has_address(self) -> bool:
        """Check if any address fields are populated."""
        return bool(
            self.address_line_1
            or self.address_line_2
            or self.building_or_campus
            or self.city
            or self.state
            or self.postal_code
        )

    @property
    def has_contact_info(self) -> bool:
        """Check if any telephone, email, or address info is configured."""
        return bool(
            self.email_general
            or self.phone_primary
            or self.email_admissions
            or self.email_reception
            or self.phone_secondary
            or self.has_address
        )

    @property
    def has_social_links(self) -> bool:
        """Check if any social media URLs are populated."""
        return bool(
            self.twitter_url
            or self.linkedin_url
            or self.youtube_url
            or self.facebook_url
            or self.instagram_url
        )

    @property
    def social_links_list(self) -> list[dict]:
        """
        Return a list of configured social media link dicts.
        """
        links = []
        if self.twitter_url:
            links.append({"name": "Twitter/X", "url": self.twitter_url, "platform": "twitter"})
        if self.linkedin_url:
            links.append({"name": "LinkedIn", "url": self.linkedin_url, "platform": "linkedin"})
        if self.youtube_url:
            links.append({"name": "YouTube", "url": self.youtube_url, "platform": "youtube"})
        if self.facebook_url:
            links.append({"name": "Facebook", "url": self.facebook_url, "platform": "facebook"})
        if self.instagram_url:
            links.append({"name": "Instagram", "url": self.instagram_url, "platform": "instagram"})
        return links

    class Meta:
        verbose_name = "Site Settings"


# Alias for institutional clarity
InstitutionSettings = SiteSettings


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
