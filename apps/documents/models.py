"""
Documents app — models for DocumentCategory, DocumentIndexPage, DocumentPage,
PublicationIndexPage, PublicationPage, ReportIndexPage, ReportPage,
TenderIndexPage, TenderPage, CareerIndexPage, CareerPage.
"""

import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.models import BasePage

# ---------------------------------------------------------------------------
# DocumentCategory snippet
# ---------------------------------------------------------------------------


@register_snippet
class DocumentCategory(models.Model):
    """
    Taxonomy snippet for classifying institutional documents.
    Managed via the Wagtail snippets interface.
    """

    name = models.CharField(
        max_length=100,
        help_text="Category display name shown on the site.",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-safe identifier used for filtering (auto-populated from name).",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = "Document category"
        verbose_name_plural = "Document categories"

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# DocumentIndexPage
# ---------------------------------------------------------------------------


class DocumentIndexPage(BasePage):
    """
    Landing page that lists all published document pages.
    Supports category filtering via ?category=<slug> and pagination (15/page).
    """

    intro = RichTextField(
        blank=True,
        help_text="Optional introductory text displayed above the document listing.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    subpage_types = ["documents.DocumentPage"]
    parent_page_types = ["wagtailcore.Page"]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = "Document index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        docs_qs = (
            DocumentPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .filter(is_public=True)
            .order_by("-publication_date", "-first_published_at")
            .select_related("document_file", "thumbnail")
            .prefetch_related("categories")
        )

        # Category filter
        category_slug = request.GET.get("category", "").strip()
        active_category = None
        if category_slug:
            try:
                active_category = DocumentCategory.objects.get(slug=category_slug)
                docs_qs = docs_qs.filter(categories=active_category)
            except DocumentCategory.DoesNotExist:
                pass  # Unknown slug — show all documents

        # Pagination (15 per page)
        paginator = Paginator(docs_qs, 15)
        page_number = request.GET.get("page")
        try:
            documents_page = paginator.page(page_number)
        except PageNotAnInteger:
            documents_page = paginator.page(1)
        except EmptyPage:
            documents_page = paginator.page(paginator.num_pages)

        context["documents_page"] = documents_page
        context["documents"] = documents_page
        context["paginator"] = paginator
        context["all_categories"] = DocumentCategory.objects.all()
        context["active_category"] = active_category
        context["category_slug"] = category_slug
        context["is_htmx"] = request.headers.get("HX-Request") == "true"

        return context


# ---------------------------------------------------------------------------
# DocumentPage
# ---------------------------------------------------------------------------


class DocumentPage(BasePage):
    """
    Individual document page representing a downloadable institutional document.

    The document_file field links to Wagtail's public document collection.
    For access-restricted documents, place the source document in a restricted
    Wagtail collection and set is_public=False so it is excluded from listings.
    True access control requires Wagtail collection permissions — see:
    https://docs.wagtail.org/en/stable/topics/permissions.html#collection-permissions
    """

    DOCUMENT_TYPE_CHOICES = [
        ("report", "Report"),
        ("policy", "Policy"),
        ("form", "Form"),
        ("circular", "Circular"),
        ("notice", "Notice"),
        ("annual_report", "Annual Report"),
        ("other", "Other"),
    ]

    description = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief description of the document (up to 500 characters).",
    )
    document_type = models.CharField(
        max_length=30,
        choices=DOCUMENT_TYPE_CHOICES,
        default="other",
        help_text="Classification for filtering and display.",
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date the document was officially published or released.",
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text="Issuing department or office.",
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Document version string (e.g. 'v2.1', 'Rev 3').",
    )
    language = models.CharField(
        max_length=50,
        blank=True,
        default="English",
        help_text="Primary language of the document.",
    )
    document_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=(
            "Uploadable document file from the Wagtail document library. "
            "For restricted access, use a protected Wagtail collection and "
            "set 'Is public' to False on this page."
        ),
    )
    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional cover or preview thumbnail image for listings.",
    )
    is_public = models.BooleanField(
        default=True,
        help_text=(
            "Public documents appear in the document listing. "
            "Private documents are hidden from public listings but remain "
            "accessible via direct URL. Use Wagtail collection permissions "
            "for true access restriction."
        ),
    )
    categories = models.ManyToManyField(
        DocumentCategory,
        blank=True,
        related_name="document_pages",
        help_text="One or more categories this document belongs to.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("description"),
                FieldPanel("document_type"),
                FieldPanel("publication_date"),
            ],
            heading="Document details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("department"),
                FieldPanel("version"),
                FieldPanel("language"),
                FieldPanel("categories"),
            ],
            heading="Metadata",
        ),
        MultiFieldPanel(
            [
                FieldPanel("document_file"),
                FieldPanel("thumbnail"),
                FieldPanel("is_public"),
            ],
            heading="File & visibility",
        ),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["documents.DocumentIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("description"),
        index.SearchField("department"),
        index.FilterField("document_type"),
        index.FilterField("publication_date"),
        index.FilterField("is_public"),
    ]

    class Meta:
        verbose_name = "Document page"
        verbose_name_plural = "Document pages"
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        return self.title


# ---------------------------------------------------------------------------
# PublicationIndexPage
# ---------------------------------------------------------------------------


class PublicationIndexPage(BasePage):
    """
    Landing page listing all published academic/institutional publications,
    ordered by publication year descending.
    """

    intro = RichTextField(
        blank=True,
        help_text="Optional introductory text displayed above the publications listing.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    subpage_types = ["documents.PublicationPage"]
    parent_page_types = ["wagtailcore.Page"]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = "Publication index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        publications_qs = (
            PublicationPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .order_by("-publication_year", "-first_published_at")
            .select_related("document_file")
        )

        # Group publications by year for display
        pubs_by_year: dict[int, list] = {}
        for pub in publications_qs:
            pubs_by_year.setdefault(pub.publication_year, []).append(pub)

        # Sorted list of (year, publications) tuples for template iteration
        context["publications_by_year"] = sorted(
            pubs_by_year.items(), key=lambda t: t[0], reverse=True
        )
        context["total_publications"] = publications_qs.count()

        return context


# ---------------------------------------------------------------------------
# PublicationPage
# ---------------------------------------------------------------------------


class PublicationPage(BasePage):
    """
    Individual academic or institutional publication page.
    """

    PUBLICATION_TYPE_CHOICES = [
        ("journal_article", "Journal Article"),
        ("conference_paper", "Conference Paper"),
        ("book", "Book"),
        ("book_chapter", "Book Chapter"),
        ("report", "Report"),
        ("thesis", "Thesis"),
        ("other", "Other"),
    ]

    authors = models.CharField(
        max_length=400,
        help_text="Author(s) — separate multiple names with commas or semicolons.",
    )
    publication_year = models.PositiveSmallIntegerField(
        db_index=True,
        help_text="Four-digit publication year.",
    )
    journal_or_publisher = models.CharField(
        max_length=300,
        blank=True,
        help_text="Journal name, conference name, or publisher.",
    )
    doi_or_url = models.URLField(
        blank=True,
        help_text="Digital Object Identifier (DOI) link or external publisher URL.",
    )
    abstract = models.TextField(
        blank=True,
        help_text="Publication abstract or summary.",
    )
    keywords = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated keywords for search and discovery.",
    )
    document_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Full-text PDF or document file, if available.",
    )
    publication_type = models.CharField(
        max_length=30,
        choices=PUBLICATION_TYPE_CHOICES,
        default="journal_article",
        help_text="Classification of the publication.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("publication_type"),
                FieldPanel("authors"),
                FieldPanel("publication_year"),
                FieldPanel("journal_or_publisher"),
                FieldPanel("doi_or_url"),
            ],
            heading="Publication details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("abstract"),
                FieldPanel("keywords"),
            ],
            heading="Abstract & keywords",
        ),
        FieldPanel("document_file"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["documents.PublicationIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("authors", boost=2),
        index.SearchField("abstract"),
        index.SearchField("keywords"),
        index.SearchField("journal_or_publisher"),
        index.FilterField("publication_year"),
        index.FilterField("publication_type"),
    ]

    class Meta:
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ["-publication_year"]

    def __str__(self) -> str:
        return self.title

    @property
    def keyword_list(self) -> list[str]:
        """Return keywords as a split list for template rendering."""
        if not self.keywords:
            return []
        return [k.strip() for k in self.keywords.split(",") if k.strip()]


# ---------------------------------------------------------------------------
# ReportIndexPage
# ---------------------------------------------------------------------------


class ReportIndexPage(BasePage):
    """
    Landing page listing institutional annual and periodic reports.
    """

    content_panels = BasePage.content_panels

    promote_panels = BasePage.promote_panels

    subpage_types = ["documents.ReportPage"]
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Report index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        context["reports"] = (
            ReportPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .order_by("-report_year", "-first_published_at")
            .select_related("document_file", "report_image")
        )

        return context


# ---------------------------------------------------------------------------
# ReportPage
# ---------------------------------------------------------------------------


class ReportPage(BasePage):
    """
    Individual institutional report page with downloadable document.
    """

    report_year = models.PositiveSmallIntegerField(
        db_index=True,
        help_text="Four-digit year this report covers.",
    )
    summary = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief summary of the report (up to 500 characters).",
    )
    document_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Downloadable report file (PDF recommended).",
    )
    report_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Cover image or representative illustration for the report.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("report_year"),
                FieldPanel("summary"),
            ],
            heading="Report details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("report_image"),
                FieldPanel("document_file"),
            ],
            heading="Media & file",
        ),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["documents.ReportIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.FilterField("report_year"),
    ]

    class Meta:
        verbose_name = "Report"
        verbose_name_plural = "Reports"
        ordering = ["-report_year"]

    def __str__(self) -> str:
        return self.title


# ---------------------------------------------------------------------------
# TenderIndexPage
# ---------------------------------------------------------------------------


class TenderIndexPage(BasePage):
    """
    Landing page listing open and recent institutional tenders.
    """

    content_panels = BasePage.content_panels

    promote_panels = BasePage.promote_panels

    subpage_types = ["documents.TenderPage"]
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Tender index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        base_qs = (
            TenderPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .select_related("document_file")
        )

        context["tenders"] = base_qs
        context["open_tenders"] = base_qs.filter(status="open").order_by(
            "closing_date", "-first_published_at"
        )
        context["closed_tenders"] = base_qs.exclude(status="open").order_by(
            "-closing_date", "-first_published_at"
        )
        context["today"] = datetime.date.today()

        return context


# ---------------------------------------------------------------------------
# TenderPage
# ---------------------------------------------------------------------------


class TenderPage(BasePage):
    """
    Individual tender notice page.
    """

    TENDER_TYPE_CHOICES = [
        ("goods", "Goods"),
        ("works", "Works"),
        ("services", "Services"),
        ("consultancy", "Consultancy"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("cancelled", "Cancelled"),
        ("awarded", "Awarded"),
    ]

    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Official tender reference or notice number.",
    )
    tender_type = models.CharField(
        max_length=20,
        choices=TENDER_TYPE_CHOICES,
        default="other",
        help_text="Procurement category for this tender.",
    )
    description = RichTextField(
        blank=True,
        help_text="Full tender description, scope, and terms.",
    )
    opening_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which tender documents become available.",
    )
    closing_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Deadline for submission of bids.",
    )
    estimated_value = models.CharField(
        max_length=100,
        blank=True,
        help_text="Estimated contract value (e.g. '₹25,00,000' or 'USD 50,000').",
    )
    document_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Tender document package for download.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        db_index=True,
        help_text="Current status of this tender.",
    )
    contact_email = models.EmailField(
        blank=True,
        help_text="Contact e-mail address for tender enquiries.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("reference_number"),
                FieldPanel("tender_type"),
                FieldPanel("status"),
                FieldPanel("estimated_value"),
            ],
            heading="Tender details",
        ),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("opening_date"), FieldPanel("closing_date")]),
                FieldPanel("contact_email"),
            ],
            heading="Dates & contact",
        ),
        FieldPanel("document_file"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["documents.TenderIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("reference_number"),
        index.SearchField("description"),
        index.FilterField("status"),
        index.FilterField("closing_date"),
        index.FilterField("tender_type"),
    ]

    class Meta:
        verbose_name = "Tender"
        verbose_name_plural = "Tenders"
        ordering = ["-closing_date"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_open(self) -> bool:
        """Return True if this tender is currently open for bids."""
        if self.status != "open":
            return False
        today = datetime.date.today()
        return not (self.closing_date and today > self.closing_date)

    @property
    def days_remaining(self) -> int | None:
        """Days remaining until the closing date, or None if not set/closed."""
        if not self.closing_date or not self.is_open:
            return None
        return (self.closing_date - datetime.date.today()).days


# ---------------------------------------------------------------------------
# CareerIndexPage
# ---------------------------------------------------------------------------


class CareerIndexPage(BasePage):
    """
    Landing page listing open career and recruitment opportunities.
    """

    content_panels = BasePage.content_panels

    promote_panels = BasePage.promote_panels

    subpage_types = ["documents.CareerPage"]
    parent_page_types = ["wagtailcore.Page"]

    class Meta:
        verbose_name = "Career index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        base_qs = (
            CareerPage.objects.live()
            .public()
            .visible()
            .descendant_of(self)
            .select_related("document_file")
        )

        context["careers"] = base_qs
        context["open_positions"] = base_qs.filter(status="open").order_by(
            "closing_date", "-first_published_at"
        )
        context["closed_positions"] = base_qs.exclude(status="open").order_by(
            "-closing_date", "-first_published_at"
        )
        context["today"] = datetime.date.today()

        return context


# ---------------------------------------------------------------------------
# CareerPage
# ---------------------------------------------------------------------------


class CareerPage(BasePage):
    """
    Individual career/job posting page.
    """

    POSITION_TYPE_CHOICES = [
        ("faculty", "Faculty"),
        ("staff", "Staff"),
        ("research", "Research"),
        ("postdoc", "Post-Doctoral"),
        ("phd", "PhD"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("closed", "Closed"),
        ("filled", "Filled"),
    ]

    position_type = models.CharField(
        max_length=20,
        choices=POSITION_TYPE_CHOICES,
        default="other",
        help_text="Type of position being advertised.",
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text="Hiring department or school.",
    )
    description = RichTextField(
        blank=True,
        help_text="Full position description, responsibilities, and context.",
    )
    qualifications = RichTextField(
        blank=True,
        help_text="Required and preferred qualifications for applicants.",
    )
    closing_date = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Application deadline.",
    )
    application_url = models.URLField(
        blank=True,
        help_text="External application portal URL.",
    )
    application_email = models.EmailField(
        blank=True,
        help_text="E-mail address to send applications to (if no portal URL).",
    )
    document_file = models.ForeignKey(
        "wagtaildocs.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Detailed job description or advertisement document.",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
        db_index=True,
        help_text="Current recruitment status.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("position_type"),
                FieldPanel("department"),
                FieldPanel("status"),
                FieldPanel("closing_date"),
            ],
            heading="Position details",
        ),
        FieldPanel("description"),
        FieldPanel("qualifications"),
        MultiFieldPanel(
            [
                FieldPanel("application_url"),
                FieldPanel("application_email"),
                FieldPanel("document_file"),
            ],
            heading="Application",
        ),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["documents.CareerIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("description"),
        index.SearchField("qualifications"),
        index.SearchField("department"),
        index.FilterField("status"),
        index.FilterField("position_type"),
        index.FilterField("closing_date"),
    ]

    class Meta:
        verbose_name = "Career posting"
        verbose_name_plural = "Career postings"
        ordering = ["closing_date", "-first_published_at"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_open(self) -> bool:
        """Return True if this position is currently open for applications."""
        if self.status != "open":
            return False
        today = datetime.date.today()
        return not (self.closing_date and today > self.closing_date)

    @property
    def days_remaining(self) -> int | None:
        """Days remaining until the closing date, or None if not set/closed."""
        if not self.closing_date or not self.is_open:
            return None
        return (self.closing_date - datetime.date.today()).days
