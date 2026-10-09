"""
Core app — base models, reusable blocks, shared utilities, and scheduled visibility system.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.http import Http404
from django.utils import timezone
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.models import Page, PageManager, PageQuerySet
from wagtail.search import index


# ---------------------------------------------------------------------------
# Scheduled Visibility QuerySets & Mixins
# ---------------------------------------------------------------------------


class ScheduledVisibilityQuerySetMixin:
    """
    Reusable QuerySet methods for scheduled visibility filtering.
    """

    def visible(self, current_time=None):
        """
        Filter records eligible for public display at current_time:
        is_active=True
        AND display_start <= current_time
        AND (display_end IS NULL OR display_end > current_time)
        """
        if current_time is None:
            current_time = timezone.now()
        return self.filter(
            is_active=True,
            display_start__lte=current_time,
        ).filter(
            models.Q(display_end__isnull=True) | models.Q(display_end__gt=current_time)
        )

    def filter_visible(self, current_time=None):
        """Alias for visible()."""
        return self.visible(current_time=current_time)

    def active(self):
        """Filter records with is_active=True."""
        return self.filter(is_active=True)

    def inactive(self):
        """Filter records with is_active=False."""
        return self.filter(is_active=False)

    def scheduled(self, current_time=None):
        """Filter records scheduled for future display."""
        if current_time is None:
            current_time = timezone.now()
        return self.filter(is_active=True, display_start__gt=current_time)

    def expired(self, current_time=None):
        """Filter records whose display_end has passed."""
        if current_time is None:
            current_time = timezone.now()
        return self.filter(
            is_active=True,
            display_end__isnull=False,
            display_end__lte=current_time,
        )


class ScheduledVisibilityQuerySet(ScheduledVisibilityQuerySetMixin, models.QuerySet):
    """Standard Django QuerySet with scheduled visibility filters."""

    pass


class ScheduledVisibilityPageQuerySet(ScheduledVisibilityQuerySetMixin, PageQuerySet):
    """Wagtail PageQuerySet with scheduled visibility filters."""

    pass


# ---------------------------------------------------------------------------
# Visibility Status Constants
# ---------------------------------------------------------------------------


class VisibilityStatus:
    INACTIVE = "inactive"
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID_SCHEDULE = "invalid_schedule"


# ---------------------------------------------------------------------------
# ScheduledVisibilityModel (Abstract base for any scheduled Django content)
# ---------------------------------------------------------------------------


class ScheduledVisibilityModel(models.Model):
    """
    Abstract model providing shared content visibility and scheduling fields.
    Applies consistent rules across all public content models.
    """

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active",
        help_text="Enable or disable this content. Inactive content is hidden from all public views.",
    )
    display_start = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="Display start",
        help_text="Date and time from which this content becomes eligible for display.",
    )
    display_end = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Display end",
        help_text="Optional date and time after which this content is no longer displayed. Leave blank for indefinite display.",
    )

    objects = ScheduledVisibilityQuerySet.as_manager()

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        if self.display_start and self.display_end:
            if self.display_end <= self.display_start:
                raise ValidationError(
                    {
                        "display_end": "Display end date & time must be strictly later than display start date & time."
                    }
                )

    @property
    def is_currently_visible(self) -> bool:
        """Check if this record is currently eligible for public display."""
        if not self.is_active:
            return False
        now = timezone.now()
        if self.display_start and self.display_start > now:
            return False
        if self.display_end and self.display_end <= now:
            return False
        return True

    @property
    def visibility_status(self) -> str:
        """Return calculated visibility status string."""
        if self.display_end and self.display_start and self.display_end <= self.display_start:
            return VisibilityStatus.INVALID_SCHEDULE
        if not self.is_active:
            return VisibilityStatus.INACTIVE
        now = timezone.now()
        if self.display_start and self.display_start > now:
            return VisibilityStatus.SCHEDULED
        if self.display_end and self.display_end <= now:
            return VisibilityStatus.EXPIRED
        return VisibilityStatus.ACTIVE

    @property
    def visibility_status_display(self) -> str:
        """Return human-readable status label."""
        labels = {
            VisibilityStatus.INACTIVE: "Inactive",
            VisibilityStatus.SCHEDULED: "Scheduled",
            VisibilityStatus.ACTIVE: "Active (Visible)",
            VisibilityStatus.EXPIRED: "Expired",
            VisibilityStatus.INVALID_SCHEDULE: "Invalid Schedule",
        }
        return labels.get(self.visibility_status, "Unknown")

    @property
    def visibility_badge_class(self) -> str:
        """Return DaisyUI badge CSS class for admin or template display."""
        classes = {
            VisibilityStatus.INACTIVE: "badge-neutral",
            VisibilityStatus.SCHEDULED: "badge-info",
            VisibilityStatus.ACTIVE: "badge-success",
            VisibilityStatus.EXPIRED: "badge-ghost",
            VisibilityStatus.INVALID_SCHEDULE: "badge-error",
        }
        return classes.get(self.visibility_status, "badge-neutral")


# ---------------------------------------------------------------------------
# BasePage (Abstract base page for all institutional Wagtail pages)
# ---------------------------------------------------------------------------


class BasePage(ScheduledVisibilityModel, Page):
    """
    Abstract base page with SEO, metadata, and scheduled visibility fields.
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

    objects = PageManager.from_queryset(ScheduledVisibilityPageQuerySet)()

    visibility_panels = [
        MultiFieldPanel(
            [
                FieldPanel("is_active"),
                FieldRowPanel(
                    [
                        FieldPanel("display_start"),
                        FieldPanel("display_end"),
                    ]
                ),
            ],
            heading="Visibility and Scheduling",
        ),
    ]

    promote_panels = (
        Page.promote_panels
        + visibility_panels
        + [
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
    )

    search_fields = Page.search_fields + [
        index.SearchField("meta_description"),
        index.FilterField("is_active"),
        index.FilterField("display_start"),
        index.FilterField("display_end"),
    ]

    def serve(self, request, *args, **kwargs):
        """
        Enforce scheduled visibility on direct page requests.
        Hidden/inactive/scheduled/expired pages return 404.
        """
        if not self.is_currently_visible:
            raise Http404("This page is not currently available for public viewing.")
        return super().serve(request, *args, **kwargs)

    def get_sitemap_urls(self, request=None):
        """Exclude non-visible pages from sitemap.xml."""
        if not self.is_currently_visible:
            return []
        return super().get_sitemap_urls(request=request)

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
