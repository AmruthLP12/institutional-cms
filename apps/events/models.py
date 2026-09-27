"""
Events app — models for EventCategory snippet, EventIndexPage, and EventPage.
"""

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage


@register_snippet
class EventCategory(models.Model):
    """
    Taxonomy snippet for classifying events (e.g. Workshop, Seminar, Conference).
    Editors can manage categories independently from the Wagtail snippets menu.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"


class EventIndexPage(BasePage):
    """
    Landing page that lists all institutional events.

    Supports tabbed browsing between upcoming and past events,
    with lazy-loading of past events via HTMX and URL-driven
    tab state (?tab=upcoming|past) for deep-linking and pagination.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Optional introductory text shown above the event listing.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["events.EventPage"]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        now = timezone.now()
        tab = request.GET.get("tab", "upcoming")
        if tab not in ("upcoming", "past"):
            tab = "upcoming"

        upcoming_qs = (
            EventPage.objects.live()
            .child_of(self)
            .filter(start_datetime__gte=now)
            .select_related("event_image")
            .prefetch_related("categories")
            .order_by("start_datetime")
        )
        past_qs = (
            EventPage.objects.live()
            .child_of(self)
            .filter(start_datetime__lt=now)
            .select_related("event_image")
            .prefetch_related("categories")
            .order_by("-start_datetime")
        )

        from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

        page_number = request.GET.get("page", 1)

        if tab == "upcoming":
            paginator = Paginator(upcoming_qs, 10)
            try:
                paginated_events = paginator.page(page_number)
            except PageNotAnInteger:
                paginated_events = paginator.page(1)
            except EmptyPage:
                paginated_events = paginator.page(paginator.num_pages)
        else:
            paginator = Paginator(past_qs, 10)
            try:
                paginated_events = paginator.page(page_number)
            except PageNotAnInteger:
                paginated_events = paginator.page(1)
            except EmptyPage:
                paginated_events = paginator.page(paginator.num_pages)

        context["active_tab"] = tab
        context["paginated_events"] = paginated_events
        context["upcoming_count"] = upcoming_qs.count()
        context["past_count"] = past_qs.count()
        return context

    def get_template(self, request, *args, **kwargs):
        if (
            getattr(request, "htmx", False)
            or request.headers.get("HX-Request") == "true"
        ):
            return "events/_event_list_partial.html"
        return super().get_template(request, *args, **kwargs)

    class Meta:
        verbose_name = "Event Index Page"
        verbose_name_plural = "Event Index Pages"


class EventPage(BasePage):
    """
    Detail page for a single institutional event.

    Stores structured event data (dates, venue, registration) alongside
    a rich StreamField body, contact details, and category tagging.
    Event pages must be children of an EventIndexPage.
    """

    # ------------------------------------------------------------------ #
    # Core event fields                                                    #
    # ------------------------------------------------------------------ #

    summary = models.TextField(
        max_length=500,
        blank=True,
        help_text="Short teaser text for listings and social cards (max 500 characters).",
    )
    description = StreamField(
        STANDARD_BODY_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name="Event description",
        help_text="Full event description, agenda, speaker bios, etc.",
    )

    # ------------------------------------------------------------------ #
    # Date & time                                                          #
    # ------------------------------------------------------------------ #

    start_datetime = models.DateTimeField(
        db_index=True,
        verbose_name="Start date & time",
    )
    end_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="End date & time",
    )

    # ------------------------------------------------------------------ #
    # Location                                                             #
    # ------------------------------------------------------------------ #

    location_name = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Venue name",
        help_text="e.g. 'Main Auditorium, Nakashara Campus'",
    )
    location_address = models.TextField(
        blank=True,
        verbose_name="Full address",
        help_text="Street address shown on the event detail page.",
    )

    # ------------------------------------------------------------------ #
    # Registration                                                         #
    # ------------------------------------------------------------------ #

    registration_url = models.URLField(
        blank=True,
        verbose_name="Registration URL",
        help_text="External registration link (Eventbrite, Google Form, etc.).",
    )
    is_registration_closed = models.BooleanField(
        default=False,
        verbose_name="Registration closed",
        help_text="Tick this to replace the registration button with a 'Closed' notice.",
    )

    # ------------------------------------------------------------------ #
    # Media                                                                #
    # ------------------------------------------------------------------ #

    event_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Event image",
        help_text="Hero / cover image for the event (recommended 1600×900 px).",
    )

    # ------------------------------------------------------------------ #
    # Taxonomy                                                             #
    # ------------------------------------------------------------------ #

    categories = models.ManyToManyField(
        EventCategory,
        blank=True,
        related_name="events",
        verbose_name="Categories",
    )

    # ------------------------------------------------------------------ #
    # Contact information                                                  #
    # ------------------------------------------------------------------ #

    contact_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Contact person",
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Contact email",
    )
    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Contact phone",
    )

    # ------------------------------------------------------------------ #
    # Panels                                                               #
    # ------------------------------------------------------------------ #

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("summary"),
                FieldPanel("event_image"),
                FieldPanel("categories"),
            ],
            heading="Overview",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel("start_datetime"), FieldPanel("end_datetime")]
                ),
            ],
            heading="Date & time",
        ),
        MultiFieldPanel(
            [
                FieldPanel("location_name"),
                FieldPanel("location_address"),
            ],
            heading="Location",
        ),
        MultiFieldPanel(
            [
                FieldPanel("registration_url"),
                FieldPanel("is_registration_closed"),
            ],
            heading="Registration",
        ),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("contact_name"),
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
            ],
            heading="Contact",
        ),
    ]

    promote_panels = BasePage.promote_panels

    # ------------------------------------------------------------------ #
    # Search & hierarchy                                                   #
    # ------------------------------------------------------------------ #

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("description"),
        index.SearchField("location_name"),
    ]

    parent_page_types = ["events.EventIndexPage"]
    subpage_types = []

    # ------------------------------------------------------------------ #
    # Properties & helpers                                                 #
    # ------------------------------------------------------------------ #

    @property
    def is_upcoming(self) -> bool:
        """Return True if the event starts in the future."""
        return self.start_datetime >= timezone.now()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["index_page"] = self.get_parent().specific
        return context

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Event Page"
        verbose_name_plural = "Event Pages"
        ordering = ["-start_datetime"]
