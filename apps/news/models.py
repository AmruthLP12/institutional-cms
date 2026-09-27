"""
News app — models for NewsIndexPage, NewsPage, and NewsCategory snippet.
"""

import datetime

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage

# ---------------------------------------------------------------------------
# NewsCategory snippet
# ---------------------------------------------------------------------------


@register_snippet
class NewsCategory(models.Model):
    """
    Taxonomy snippet for classifying news articles.
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
    icon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional icon image displayed alongside the category label.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("icon"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = "News category"
        verbose_name_plural = "News categories"

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# NewsIndexPage
# ---------------------------------------------------------------------------


class NewsIndexPage(BasePage):
    """
    Landing page that lists all published news articles.
    Supports category filtering via ?category=<slug> and pagination.
    """

    intro = RichTextField(
        blank=True,
        help_text="Optional introductory text displayed above the news grid.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = ["news.NewsPage"]
    parent_page_types = ["wagtailcore.Page"]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = "News index page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        news_qs = (
            NewsPage.objects.live()
            .public()
            .descendant_of(self)
            .order_by("-publication_date", "-first_published_at")
            .select_related("featured_image", "owner")
            .prefetch_related("categories")
        )

        # Category filter
        category_slug = request.GET.get("category", "").strip()
        active_category = None
        if category_slug:
            try:
                active_category = NewsCategory.objects.get(slug=category_slug)
                news_qs = news_qs.filter(categories=active_category)
            except NewsCategory.DoesNotExist:
                pass  # Unknown slug — show all articles

        # Pagination
        paginator = Paginator(news_qs, 12)
        page_number = request.GET.get("page")
        try:
            news_page = paginator.page(page_number)
        except PageNotAnInteger:
            news_page = paginator.page(1)
        except EmptyPage:
            news_page = paginator.page(paginator.num_pages)

        context["news_items"] = news_page
        context["paginator"] = paginator
        context["all_categories"] = NewsCategory.objects.all()
        context["active_category"] = active_category
        context["category_slug"] = category_slug

        # Flag for HTMX partial rendering
        context["is_htmx"] = (
            getattr(request, "htmx", False)
            or request.headers.get("HX-Request") == "true"
        )

        return context

    def get_template(self, request, *args, **kwargs):
        if (
            getattr(request, "htmx", False)
            or request.headers.get("HX-Request") == "true"
        ):
            return "news/partials/news_grid.html"
        return super().get_template(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# NewsPage
# ---------------------------------------------------------------------------


class NewsPage(BasePage):
    """
    Individual news article page.
    """

    headline = models.CharField(
        max_length=300,
        help_text="Article headline displayed as the main title.",
    )
    summary = models.TextField(
        blank=True,
        max_length=500,
        help_text="Brief summary for listing pages (up to 500 characters).",
    )
    body = StreamField(
        STANDARD_BODY_BLOCKS,
        use_json_field=True,
        blank=True,
        help_text="Main article body content.",
    )
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero image for the article (used in listings and social sharing).",
    )
    author_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Author display name shown on the article.",
    )
    publication_date = models.DateField(
        db_index=True,
        default=datetime.date.today,
        help_text="Date shown publicly on the article and used for sorting.",
    )
    categories = models.ManyToManyField(
        NewsCategory,
        blank=True,
        related_name="news_pages",
        help_text="One or more categories this article belongs to.",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("headline"),
                FieldPanel("summary"),
            ],
            heading="Article details",
        ),
        MultiFieldPanel(
            [
                FieldPanel("featured_image"),
                FieldPanel("author_name"),
                FieldPanel("publication_date"),
                FieldPanel("categories"),
            ],
            heading="Metadata",
        ),
        FieldPanel("body"),
    ]

    promote_panels = BasePage.promote_panels

    parent_page_types = ["news.NewsIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("headline", boost=2),
        index.SearchField("summary"),
        index.SearchField("body"),
        index.FilterField("publication_date"),
    ]

    class Meta:
        verbose_name = "News article"
        verbose_name_plural = "News articles"
        ordering = ["-publication_date"]

    def __str__(self) -> str:
        return self.headline

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Collect category PKs for this article
        category_pks = list(self.categories.values_list("pk", flat=True))

        # Up to 3 most recent published articles in the same categories,
        # excluding the current article.
        related_posts = (
            NewsPage.objects.live()
            .public()
            .filter(categories__in=category_pks)
            .exclude(pk=self.pk)
            .order_by("-publication_date", "-first_published_at")
            .select_related("featured_image")
            .prefetch_related("categories")
            .distinct()[:3]
        )

        context["related_posts"] = related_posts

        # Absolute URL for social sharing
        context["absolute_url"] = request.build_absolute_uri(self.url)

        return context
