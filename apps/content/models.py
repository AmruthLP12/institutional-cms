"""
Content app models — StandardPage, ContactPage, AnnouncementPage, NoticePage.
"""

from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage


class StandardPage(BasePage):
    """
    General-purpose institutional content page.
    Suitable for About, Leadership overview, Academics overview, etc.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Short introduction shown prominently at the top of the page.",
    )
    body = StreamField(
        STANDARD_BODY_BLOCKS,
        blank=True,
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Standard page"


class ContactFormField(AbstractFormField):
    """Field within a contact form."""

    page = ParentalKey(
        "content.ContactPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class ContactPage(AbstractEmailForm, BasePage):
    """
    Contact page with an email form, address details, and a map placeholder.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
    )
    thank_you_text = RichTextField(
        blank=True,
        help_text="Message shown after form submission.",
    )
    address_block = RichTextField(
        blank=True,
        help_text="Formatted address for display.",
    )
    phone_primary = models.CharField(max_length=30, blank=True)
    phone_secondary = models.CharField(max_length=30, blank=True)
    email_contact = models.EmailField(blank=True)
    map_embed_url = models.URLField(
        blank=True,
        help_text="Google Maps embed URL (no JavaScript tracking version preferred).",
    )

    from_address = models.EmailField(
        verbose_name="From address",
        help_text="The email address form submissions are sent from.",
    )
    to_address = models.EmailField(
        verbose_name="To address",
        help_text="Email address that receives submitted forms.",
    )
    subject = models.CharField(
        max_length=200,
        verbose_name="Subject",
        default="Contact form submission — Nakashara",
    )

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                FieldPanel("address_block"),
                FieldPanel("phone_primary"),
                FieldPanel("phone_secondary"),
                FieldPanel("email_contact"),
                FieldPanel("map_embed_url"),
            ],
            heading="Contact details",
        ),
        FieldPanel("thank_you_text"),
        MultiFieldPanel(
            [
                FieldPanel("from_address"),
                FieldPanel("to_address"),
                FieldPanel("subject"),
            ],
            heading="Email settings",
        ),
    ]

    promote_panels = BasePage.promote_panels

    template = "content/contact_page.html"
    landing_page_template = "content/contact_page_landing.html"

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = "Contact page"


class AnnouncementPage(BasePage):
    """
    Short announcement — a brief notice posted by the institution.
    Typically visible on the homepage and announcements listing.
    """

    summary = models.TextField(
        max_length=500,
        help_text="Brief announcement text (shown on listings and homepage).",
    )
    body = StreamField(
        STANDARD_BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        help_text="Optional extended content.",
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date after which this announcement should no longer be prominently displayed.",
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text="Pin this announcement to the top of listings.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("summary"),
        FieldPanel("body"),
        FieldPanel("expiry_date"),
        FieldPanel("is_pinned"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    @property
    def is_current(self) -> bool:
        return not (self.expiry_date and self.expiry_date < timezone.now().date())

    class Meta:
        verbose_name = "Announcement"
        verbose_name_plural = "Announcements"


class AnnouncementIndexPage(BasePage):
    """Listing page for announcements."""

    intro = RichTextField(blank=True, features=["bold", "italic"])

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    subpage_types = ["content.AnnouncementPage"]
    parent_page_types = ["wagtailcore.Page"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from django.core.paginator import Paginator

        announcements = (
            AnnouncementPage.objects.live()
            .public()
            .order_by("-is_pinned", "-first_published_at")
        )
        paginator = Paginator(announcements, 15)
        page_number = request.GET.get("page", 1)
        context["announcements"] = paginator.get_page(page_number)
        return context

    class Meta:
        verbose_name = "Announcements index"


class NoticePage(BasePage):
    """
    Formal institutional notice — more structured than an announcement.
    """

    notice_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official notice reference number (e.g. REG/2026/001).",
    )
    summary = models.TextField(max_length=500, blank=True)
    body = StreamField(STANDARD_BODY_BLOCKS, blank=True, use_json_field=True)
    notice_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    issuing_authority = models.CharField(max_length=200, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("notice_number"),
        FieldPanel("summary"),
        FieldPanel("body"),
        FieldPanel("notice_date"),
        FieldPanel("expiry_date"),
        FieldPanel("issuing_authority"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"


class NoticeIndexPage(BasePage):
    """Listing page for notices."""

    intro = RichTextField(blank=True, features=["bold", "italic"])

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    subpage_types = ["content.NoticePage"]
    parent_page_types = ["wagtailcore.Page"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        from django.core.paginator import Paginator

        notices = (
            NoticePage.objects.live()
            .public()
            .order_by("-notice_date", "-first_published_at")
        )
        paginator = Paginator(notices, 15)
        page_number = request.GET.get("page", 1)
        context["notices"] = paginator.get_page(page_number)
        return context

    class Meta:
        verbose_name = "Notices index"
