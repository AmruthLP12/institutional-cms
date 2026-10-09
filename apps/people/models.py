"""
People app — models for the Nakashara institutional directory.

Page hierarchy:
    PersonIndexPage  (child of root / any top-level Page)
    └── PersonPage   (each individual profile)

Snippets:
    PersonCategory   (Faculty, Staff, Researcher, Leadership, etc.)
"""

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.text import slugify
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.blocks import ImageBlock, RichBodyBlock
from apps.core.models import BasePage

# ---------------------------------------------------------------------------
# Snippet: PersonCategory
# ---------------------------------------------------------------------------


@register_snippet
class PersonCategory(models.Model):
    """
    Taxonomy snippet for grouping people (Faculty, Staff, Researcher, etc.).
    Registered as a Wagtail snippet so editors can manage categories from
    the Snippets menu without a dedicated page.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name, e.g. 'Faculty', 'Staff', 'Researcher', 'Leadership'.",
    )
    slug = models.SlugField(
        max_length=110,
        unique=True,
        blank=True,
        help_text="URL-safe identifier auto-generated from name. Used for filtering.",
    )
    ordering = models.PositiveSmallIntegerField(
        default=0,
        help_text="Lower numbers appear first in category lists.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("ordering"),
    ]

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Person Category"
        verbose_name_plural = "Person Categories"
        ordering = ["ordering", "name"]


# ---------------------------------------------------------------------------
# Page: PersonIndexPage
# ---------------------------------------------------------------------------


class PersonIndexPage(BasePage):
    """
    Landing page that lists all PersonPages.

    Supports:
    - Optional ?category=<slug> filter to show a single category's people.
    - ?page=<N> pagination at 20 people per page.
    - People are grouped by PersonCategory when no filter is active.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Optional introductory text shown above the people grid.",
    )

    # -----------------------------------------------------------------------
    # Page constraints
    # -----------------------------------------------------------------------
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["people.PersonPage"]

    # -----------------------------------------------------------------------
    # Wagtail admin panels
    # -----------------------------------------------------------------------
    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    # -----------------------------------------------------------------------
    # Search
    # -----------------------------------------------------------------------
    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    # -----------------------------------------------------------------------
    # Context
    # -----------------------------------------------------------------------
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        category_slug = request.GET.get("category", "").strip()
        page_number = request.GET.get("page", 1)

        # Base queryset — only live, published, visible PersonPages that are children.
        people_qs = (
            PersonPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .select_related("department", "profile_photo")
            .prefetch_related("categories")
            .order_by("ordering", "last_name", "first_name")
        )

        # All categories that have at least one live person, for filter pills.
        all_categories = (
            PersonCategory.objects.filter(personpage__in=people_qs)
            .distinct()
            .order_by("ordering", "name")
        )

        active_category = None
        if category_slug:
            try:
                active_category = PersonCategory.objects.get(slug=category_slug)
                people_qs = people_qs.filter(categories=active_category)
            except PersonCategory.DoesNotExist:
                pass  # Invalid slug — silently fall back to all people.

        # Paginate
        paginator = Paginator(people_qs, 20)
        try:
            people_page = paginator.page(page_number)
        except PageNotAnInteger:
            people_page = paginator.page(1)
        except EmptyPage:
            people_page = paginator.page(paginator.num_pages)

        # Grouped view (only when no category filter is active)
        grouped_people = []
        if not active_category:
            # Collect each category and its members, then append uncategorised.
            seen_ids = set()
            for cat in all_categories:
                members = [
                    p for p in people_page.object_list if cat in p.categories.all()
                ]
                if members:
                    grouped_people.append({"category": cat, "people": members})
                    seen_ids.update(p.pk for p in members)
            uncategorised = [p for p in people_page.object_list if p.pk not in seen_ids]
            if uncategorised:
                grouped_people.append({"category": None, "people": uncategorised})

        context.update(
            {
                "people_page": people_page,
                "paginator": paginator,
                "all_categories": all_categories,
                "active_category": active_category,
                "grouped_people": grouped_people,
                "category_slug": category_slug,
            }
        )
        return context

    def get_template(self, request, *args, **kwargs):
        if (
            getattr(request, "htmx", False)
            or request.headers.get("HX-Request") == "true"
        ):
            return "people/partials/people_grid.html"
        return super().get_template(request, *args, **kwargs)

    class Meta:
        verbose_name = "Person Index Page"
        verbose_name_plural = "Person Index Pages"


# ---------------------------------------------------------------------------
# Page: PersonPage
# ---------------------------------------------------------------------------


class PersonPage(BasePage):
    """
    Individual person profile page.

    Contact information (email and phone) is shown publicly only when
    ``is_public_contact`` is True. Templates MUST respect this flag.
    """

    # -----------------------------------------------------------------------
    # Identity
    # -----------------------------------------------------------------------
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    designation = models.CharField(
        max_length=200,
        blank=True,
        help_text="Job title or role, e.g. 'Associate Professor of Economics'.",
    )

    # -----------------------------------------------------------------------
    # Relationships
    # -----------------------------------------------------------------------
    department = models.ForeignKey(
        "departments.DepartmentPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="people",
        help_text="Primary department affiliation.",
    )
    profile_photo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Headshot image. Square crop recommended (minimum 400×400 px).",
    )
    categories = ParentalManyToManyField(
        PersonCategory,
        blank=True,
        help_text="Select one or more categories (Faculty, Staff, Researcher, etc.).",
    )

    # -----------------------------------------------------------------------
    # Extended profile content
    # -----------------------------------------------------------------------
    biography = StreamField(
        [
            ("rich_text", RichBodyBlock()),
            ("image", ImageBlock()),
        ],
        use_json_field=True,
        blank=True,
        help_text="Full biography. Supports rich text sections and images.",
    )
    research_interests = RichTextField(
        blank=True,
        features=["bold", "italic", "link", "ol", "ul"],
        help_text="Research areas, specialisations, or academic interests.",
    )

    # -----------------------------------------------------------------------
    # Contact details (conditionally public)
    # -----------------------------------------------------------------------
    email = models.EmailField(
        blank=True,
        help_text="Shown publicly only if 'Show contact publicly' is enabled.",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        help_text="Shown publicly only if 'Show contact publicly' is enabled.",
    )
    office_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Room number, building, or campus location. Always shown publicly.",
    )
    is_public_contact = models.BooleanField(
        default=False,
        verbose_name="Show contact publicly",
        help_text=(
            "When enabled, email and phone are displayed on the public profile. "
            "Disable to keep contact details internal only."
        ),
    )

    # -----------------------------------------------------------------------
    # Display ordering
    # -----------------------------------------------------------------------
    ordering = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first within category/index listings.",
    )

    # -----------------------------------------------------------------------
    # Page constraints
    # -----------------------------------------------------------------------
    parent_page_types = ["people.PersonIndexPage"]
    subpage_types = []

    # -----------------------------------------------------------------------
    # Wagtail admin panels — tabbed interface for clarity
    # -----------------------------------------------------------------------
    identity_panels = [
        FieldRowPanel([FieldPanel("first_name"), FieldPanel("last_name")]),
        FieldPanel("designation"),
        FieldPanel("department"),
        FieldPanel("categories"),
        FieldPanel("profile_photo"),
        FieldPanel("ordering"),
    ]

    biography_panels = [
        FieldPanel("biography"),
        FieldPanel("research_interests"),
    ]

    contact_panels = [
        FieldPanel("is_public_contact"),
        FieldRowPanel([FieldPanel("email"), FieldPanel("phone")]),
        FieldPanel("office_location"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(
                BasePage.content_panels + identity_panels,
                heading="Profile",
            ),
            ObjectList(biography_panels, heading="Biography & Research"),
            ObjectList(contact_panels, heading="Contact"),
            ObjectList(BasePage.promote_panels, heading="SEO"),
        ]
    )

    # -----------------------------------------------------------------------
    # Search
    # -----------------------------------------------------------------------
    search_fields = BasePage.search_fields + [
        index.SearchField("first_name", boost=2),
        index.SearchField("last_name", boost=2),
        index.SearchField("designation"),
        index.SearchField("research_interests"),
        index.RelatedFields("categories", [index.SearchField("name")]),
        index.RelatedFields("department", [index.SearchField("title")]),
    ]

    # -----------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------
    @property
    def full_name(self) -> str:
        """Return concatenated first and last name."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self) -> str:
        return self.full_name

    # -----------------------------------------------------------------------
    # Context
    # -----------------------------------------------------------------------
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Provide the parent index page for breadcrumb building.
        context["index_page"] = self.get_parent().specific
        return context

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"
        ordering = ["ordering", "last_name", "first_name"]
