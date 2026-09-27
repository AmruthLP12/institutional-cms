"""
Research app models.

Provides:
  - ResearchArea      — snippet taxonomy for tagging research projects.
  - ResearchIndexPage — listing page with area filtering and pagination.
  - ResearchProjectPage — individual project detail page.
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage

# ─────────────────────────────────────────────────────────────────────────────
# Snippet: ResearchArea
# ─────────────────────────────────────────────────────────────────────────────


@register_snippet
class ResearchArea(models.Model):
    """
    Taxonomy term used to categorise research projects (e.g. 'Machine Learning',
    'Biotechnology', 'Urban Planning').
    """

    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name = "Research Area"
        verbose_name_plural = "Research Areas"


# ─────────────────────────────────────────────────────────────────────────────
# ResearchIndexPage
# ─────────────────────────────────────────────────────────────────────────────


class ResearchIndexPage(BasePage):
    """
    Root listing page that aggregates all published ResearchProjectPages.

    Supports filtering by ResearchArea via ``?area=<slug>`` and paginated
    browsing via ``?page=<n>`` (10 projects per page).
    """

    intro = RichTextField(
        blank=True,
        help_text="Optional introductory text displayed above the project grid.",
    )

    # ── Page tree ──────────────────────────────────────────────────────────
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["research.ResearchProjectPage"]

    # ── Search ─────────────────────────────────────────────────────────────
    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    # ── Panels ─────────────────────────────────────────────────────────────
    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    # ── Context ────────────────────────────────────────────────────────────
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Base queryset — live, public children ordered by start_date desc.
        projects = (
            ResearchProjectPage.objects.live()
            .public()
            .child_of(self)
            .order_by("-start_date")
            .select_related("project_image", "department")
            .prefetch_related("areas")
        )

        # Area filter.
        area_slug = request.GET.get("area", "").strip()
        active_area = None
        if area_slug:
            try:
                active_area = ResearchArea.objects.get(slug=area_slug)
                projects = projects.filter(areas=active_area)
            except ResearchArea.DoesNotExist:
                pass

        # Pagination — 10 items per page.
        paginator = Paginator(projects, 10)
        page_number = request.GET.get("page")
        try:
            projects_page = paginator.page(page_number)
        except PageNotAnInteger:
            projects_page = paginator.page(1)
        except EmptyPage:
            projects_page = paginator.page(paginator.num_pages)

        context["projects"] = projects_page
        context["paginator"] = paginator
        context["active_area"] = active_area
        context["all_areas"] = ResearchArea.objects.all()
        return context

    class Meta:
        verbose_name = "Research Index Page"
        verbose_name_plural = "Research Index Pages"


# ─────────────────────────────────────────────────────────────────────────────
# ResearchProjectPage
# ─────────────────────────────────────────────────────────────────────────────


class ResearchProjectPage(BasePage):
    """
    An individual research project with metadata, a rich description body,
    and taxonomy tags for research areas.
    """

    STATUS_ONGOING = "ongoing"
    STATUS_COMPLETED = "completed"
    STATUS_PROPOSED = "proposed"
    STATUS_SUSPENDED = "suspended"

    STATUS_CHOICES = [
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_PROPOSED, "Proposed"),
        (STATUS_SUSPENDED, "Suspended"),
    ]

    # ── Overview ───────────────────────────────────────────────────────────
    summary = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief project summary (max 500 characters) shown on listing cards.",
    )
    description = StreamField(
        STANDARD_BODY_BLOCKS,
        use_json_field=True,
        blank=True,
        help_text="Full project description — add headings, rich text, images and more.",
    )

    # ── People ─────────────────────────────────────────────────────────────
    principal_investigator = models.CharField(
        max_length=200,
        blank=True,
        help_text="Full name of the principal investigator.",
    )
    co_investigators = models.TextField(
        blank=True,
        help_text="Comma-separated names of co-investigators.",
    )

    # ── Affiliation ────────────────────────────────────────────────────────
    department = models.ForeignKey(
        "departments.DepartmentPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="research_projects",
        help_text="Primary department associated with this project.",
    )

    # ── Funding ────────────────────────────────────────────────────────────
    funding_agency = models.CharField(
        max_length=300,
        blank=True,
        help_text="Name of the funding agency or body.",
    )
    funding_amount = models.CharField(
        max_length=100,
        blank=True,
        help_text="Funding amount as a display string, e.g. '₹50 Lakhs' or '$200,000'.",
    )

    # ── Timeline ───────────────────────────────────────────────────────────
    start_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Project start date.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Project end date (leave blank if ongoing).",
    )

    # ── Status ─────────────────────────────────────────────────────────────
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ONGOING,
        help_text="Current project status.",
    )

    # ── Media ──────────────────────────────────────────────────────────────
    project_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Representative image for this project.",
    )

    # ── Taxonomy ───────────────────────────────────────────────────────────
    areas = ParentalManyToManyField(
        ResearchArea,
        blank=True,
        help_text="Research areas / themes applicable to this project.",
    )

    # ── Page tree ──────────────────────────────────────────────────────────
    parent_page_types = ["research.ResearchIndexPage"]
    subpage_types = []

    # ── Search ─────────────────────────────────────────────────────────────
    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("description"),
        index.SearchField("principal_investigator"),
        index.FilterField("status"),
        index.FilterField("start_date"),
    ]

    # ── Panels ─────────────────────────────────────────────────────────────
    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("summary"),
                FieldPanel("status"),
                FieldPanel("project_image"),
            ],
            heading="Overview",
        ),
        MultiFieldPanel(
            [
                FieldPanel("principal_investigator"),
                FieldPanel("co_investigators"),
                FieldPanel("department"),
            ],
            heading="People & Department",
        ),
        MultiFieldPanel(
            [
                FieldPanel("funding_agency"),
                FieldPanel("funding_amount"),
            ],
            heading="Funding",
        ),
        FieldRowPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
            ],
            heading="Timeline",
        ),
        FieldPanel("areas"),
        FieldPanel("description"),
    ]

    promote_panels = BasePage.promote_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(promote_panels, heading="SEO / Promote"),
        ]
    )

    # ── Properties ─────────────────────────────────────────────────────────
    @property
    def is_ongoing(self) -> bool:
        """Return True when the project status is 'ongoing'."""
        return self.status == self.STATUS_ONGOING

    # ── Context ────────────────────────────────────────────────────────────
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["areas"] = self.areas.all()
        context["co_investigator_list"] = [
            name.strip() for name in self.co_investigators.split(",") if name.strip()
        ]
        return context

    class Meta:
        ordering = ["-start_date"]
        verbose_name = "Research Project Page"
        verbose_name_plural = "Research Project Pages"
