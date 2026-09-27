"""
Departments app models.

Provides two Wagtail page types:
  - DepartmentIndexPage  — listing of all institutional departments.
  - DepartmentPage       — individual department with staff and research links.
"""

from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage


class DepartmentIndexPage(BasePage):
    """
    Root listing page for all departments.

    Intended to sit directly under the Wagtail root (or a top-level site page)
    and aggregate every published DepartmentPage as its children.
    """

    intro = RichTextField(
        blank=True,
        help_text="Optional introductory text shown above the department grid.",
    )

    # ------------------------------------------------------------------ #
    # Page tree constraints
    # ------------------------------------------------------------------ #
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["departments.DepartmentPage"]

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    # ------------------------------------------------------------------ #
    # Panels
    # ------------------------------------------------------------------ #
    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    # ------------------------------------------------------------------ #
    # Context
    # ------------------------------------------------------------------ #
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        departments = (
            DepartmentPage.objects.live()
            .public()
            .child_of(self)
            .order_by("title")
            .only(
                "id",
                "title",
                "slug",
                "short_name",
                "description",
                "contact_email",
                "contact_phone",
                "location",
            )
        )
        context["departments"] = departments
        return context

    class Meta:
        verbose_name = "Department Index Page"
        verbose_name_plural = "Department Index Pages"


class DepartmentPage(BasePage):
    """
    A single institutional department page.

    Carries contact details, leadership information, a rich body StreamField,
    and exposes related people and research projects in its context.
    """

    # ------------------------------------------------------------------ #
    # Identity
    # ------------------------------------------------------------------ #
    short_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Abbreviated name or acronym (e.g. 'CSE', 'MBA'). Used in badges.",
    )

    # ------------------------------------------------------------------ #
    # Description
    # ------------------------------------------------------------------ #
    description = RichTextField(
        blank=True,
        help_text="Short description of the department shown below the title.",
    )

    # ------------------------------------------------------------------ #
    # Contact
    # ------------------------------------------------------------------ #
    contact_email = models.EmailField(
        blank=True,
        help_text="Primary public contact e-mail address.",
    )
    contact_phone = models.CharField(
        max_length=30,
        blank=True,
        help_text="Primary public contact phone number.",
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        help_text="Physical location or building name on campus.",
    )
    website_url = models.URLField(
        blank=True,
        help_text="External or dedicated department website URL.",
    )

    # ------------------------------------------------------------------ #
    # Leadership
    # ------------------------------------------------------------------ #
    head_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Department head name.",
    )
    head_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Official title of the department head (e.g. 'Professor & Head').",
    )

    # ------------------------------------------------------------------ #
    # History
    # ------------------------------------------------------------------ #
    established_year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Year in which the department was established.",
    )

    # ------------------------------------------------------------------ #
    # Body
    # ------------------------------------------------------------------ #
    body = StreamField(
        STANDARD_BODY_BLOCKS,
        use_json_field=True,
        blank=True,
        help_text="Main page body — add headings, rich text, images, and more.",
    )

    # ------------------------------------------------------------------ #
    # Page tree constraints
    # ------------------------------------------------------------------ #
    parent_page_types = ["departments.DepartmentIndexPage"]
    subpage_types = []

    # ------------------------------------------------------------------ #
    # Search
    # ------------------------------------------------------------------ #
    search_fields = BasePage.search_fields + [
        index.SearchField("short_name"),
        index.SearchField("description"),
        index.SearchField("head_name"),
        index.FilterField("title"),
    ]

    # ------------------------------------------------------------------ #
    # Panels
    # ------------------------------------------------------------------ #
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("short_name"),
                FieldPanel("description"),
            ],
            heading="Department identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("head_name"),
                FieldPanel("head_title"),
                FieldPanel("established_year"),
            ],
            heading="Leadership & history",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
                FieldPanel("location"),
                FieldPanel("website_url"),
            ],
            heading="Contact information",
        ),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(promote_panels, heading="SEO / Promote"),
        ]
    )

    # ------------------------------------------------------------------ #
    # Context
    # ------------------------------------------------------------------ #
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Related people — guarded with try/except so the department app
        # remains functional even when the people app is not yet installed.
        try:
            from apps.people.models import PersonPage  # noqa: PLC0415

            people = (
                PersonPage.objects.live()
                .public()
                .filter(department=self)
                .order_by("last_name", "first_name")
                .select_related("profile_photo")[:10]
            )
            context["people"] = people
        except Exception:  # noqa: BLE001
            context["people"] = []

        # Related research projects — similarly guarded.
        try:
            from apps.research.models import ResearchProjectPage  # noqa: PLC0415

            research_projects = (
                ResearchProjectPage.objects.live()
                .public()
                .filter(department=self)
                .order_by("-start_date", "title")
            )
            context["research_projects"] = research_projects
        except Exception:  # noqa: BLE001
            context["research_projects"] = []

        return context

    class Meta:
        verbose_name = "Department Page"
        verbose_name_plural = "Department Pages"
