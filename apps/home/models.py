"""
Home page model — institutional homepage with structured editorial sections.
"""

from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

from apps.core.blocks import (
    STANDARD_BODY_BLOCKS,
    StatisticsBlock,
)
from apps.core.models import BasePage


class QuickLinkItem(Orderable):
    """Quick link shown in the homepage quick-links section."""

    page = ParentalKey(
        "home.HomePage", on_delete=models.CASCADE, related_name="quick_links"
    )
    label = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    link_page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    link_url = models.URLField(blank=True)
    icon_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Lucide icon name (e.g. 'file-text', 'calendar', 'users').",
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("description"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
        FieldPanel("icon_name"),
    ]

    def get_url(self) -> str:
        if self.link_page:
            return self.link_page.url
        return self.link_url or "#"


class HomePageHeroSlide(Orderable):
    """Hero carousel slide for multi-image homepage presentations."""

    page = ParentalKey(
        "home.HomePage", on_delete=models.CASCADE, related_name="hero_slides"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Slide background image (1920×800 px or wider).",
    )
    tag = models.CharField(
        max_length=100,
        blank=True,
        default="Featured Program",
        help_text="Badge label above headline (e.g. 'Academic Excellence', 'Admissions Open').",
    )
    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Slide headline (falls back to main hero headline if blank).",
    )
    subheadline = models.CharField(
        max_length=400,
        blank=True,
        help_text="Slide subheadline (falls back to main hero subheadline if blank).",
    )
    cta_label = models.CharField(max_length=100, blank=True, help_text="CTA button label.")
    cta_page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Link to an internal page.",
    )
    cta_url = models.URLField(blank=True, help_text="External URL if no page selected.")

    panels = [
        FieldPanel("image"),
        FieldPanel("tag"),
        FieldPanel("headline"),
        FieldPanel("subheadline"),
        FieldPanel("cta_label"),
        FieldPanel("cta_page"),
        FieldPanel("cta_url"),
    ]

    def get_cta_href(self) -> str:
        if self.cta_page:
            return self.cta_page.url
        return self.cta_url or "#"


class HomePage(BasePage):
    """
    Institutional homepage.

    Composed of structured editorial sections:
    - Hero (headline, subheadline, image, CTA, or multiple Carousel Slides)
    - Announcements (auto-fetched from AnnouncementPages)
    - Featured news (auto-fetched from latest NewsPages)
    - Upcoming events (auto-fetched from EventPages)
    - Research highlights (StreamField)
    - Statistics strip
    - Quick links (Orderable)
    - Notices (auto-fetched)
    """

    # Hero section (single image default or fallback)
    hero_headline = models.CharField(
        max_length=200,
        help_text="Main homepage headline.",
    )
    hero_subheadline = models.CharField(
        max_length=400,
        blank=True,
        help_text="Supporting text under the headline.",
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero background image (1920×800 px or wider). Used if no slides are added below.",
    )
    hero_image_alt = models.CharField(
        max_length=300,
        blank=True,
        help_text="Alt text for hero image.",
    )
    hero_cta_label = models.CharField(max_length=100, blank=True, default="Explore")
    hero_cta_page = models.ForeignKey(
        Page,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_cta_url = models.URLField(blank=True)

    # Statistics strip
    statistics = StreamField(
        [("statistics", StatisticsBlock())],
        blank=True,
        use_json_field=True,
        max_num=1,
    )

    # Research highlights
    research_highlights = StreamField(
        STANDARD_BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        help_text="Editorial content for the research highlights section.",
    )

    # Intro text for the page (used by meta too)
    intro = models.TextField(
        blank=True,
        max_length=500,
        help_text="Short institutional description (used in meta tags).",
    )

    # ---- Admin panels ----
    hero_panels = [
        MultiFieldPanel(
            [
                FieldPanel("hero_headline"),
                FieldPanel("hero_subheadline"),
                FieldPanel("hero_image"),
                FieldPanel("hero_image_alt"),
                FieldPanel("hero_cta_label"),
                FieldPanel("hero_cta_page"),
                FieldPanel("hero_cta_url"),
            ],
            heading="Primary Hero Information",
        ),
        InlinePanel(
            "hero_slides",
            label="Hero Carousel Slides (Multiple Images)",
            help_text="Add 2 or more slides to enable an animated hero carousel.",
        ),
    ]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        *hero_panels,
        FieldPanel("statistics"),
        InlinePanel("quick_links", label="Quick links"),
        FieldPanel("research_highlights"),
    ]

    promote_panels = BasePage.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(promote_panels, heading="SEO & Sharing"),
        ]
    )

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []  # Homepage has no children; other sections are separate page trees

    search_fields = BasePage.search_fields + [
        index.SearchField("hero_headline"),
        index.SearchField("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        now = timezone.now()

        # Latest 3 published news items
        try:
            from apps.news.models import NewsPage

            context["featured_news"] = (
                NewsPage.objects.live()
                .public()
                .visible()
                .order_by("-publication_date")
                .select_related("featured_image")
                .prefetch_related("categories")[:3]
            )
        except Exception:
            context["featured_news"] = []

        # Upcoming 3 events
        try:
            from apps.events.models import EventPage

            context["upcoming_events"] = (
                EventPage.objects.live()
                .public()
                .visible()
                .filter(start_datetime__gte=now)
                .order_by("start_datetime")
                .select_related("event_image")[:3]
            )
        except Exception:
            context["upcoming_events"] = []

        # Latest 3 announcements
        try:
            from apps.content.models import AnnouncementPage

            context["announcements"] = (
                AnnouncementPage.objects.live()
                .public()
                .visible()
                .order_by("-first_published_at")[:5]
            )
        except Exception:
            context["announcements"] = []

        # Latest 3 notices
        try:
            from apps.content.models import NoticePage

            context["notices"] = (
                NoticePage.objects.live()
                .public()
                .visible()
                .order_by("-first_published_at")[:3]
            )
        except Exception:
            context["notices"] = []

        context["quick_links"] = self.quick_links.all().select_related("link_page")

        return context

    class Meta:
        verbose_name = "Homepage"

    def hero_cta_href(self) -> str:
        if self.hero_cta_page:
            return self.hero_cta_page.url
        return self.hero_cta_url or "#"
