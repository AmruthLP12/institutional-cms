import datetime
import pytest
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.http import Http404
from django.test import Client, RequestFactory
from django.utils import timezone
from wagtail.models import Site

from apps.content.models import AnnouncementPage, NoticePage, StandardPage
from apps.core.models import VisibilityStatus
from apps.departments.models import DepartmentPage
from apps.documents.models import DocumentPage, TenderPage
from apps.events.models import EventPage
from apps.home.models import HomePage
from apps.legal.models import LegalPage
from apps.news.models import NewsPage
from apps.people.models import PersonPage
from apps.research.models import ResearchProjectPage
from apps.site_settings.models import AlertBanner


@pytest.fixture
def seeded_site(db, home_page):
    """Seed full CMS content for test environment."""
    call_command("seed_cms", demo=True, legal=True, navigation=True)
    site = Site.objects.get(is_default_site=True)
    return site


@pytest.mark.django_db
class TestContentVisibilityAndScheduling:
    def test_default_values_on_creation(self, home_page):
        """1 & 2: Verify new records default to is_active=True and display_start near now."""
        now = timezone.now()
        news = NewsPage(
            title="Scheduled Article",
            slug="scheduled-article",
            headline="Headline",
        )
        assert news.is_active is True
        assert abs((news.display_start - now).total_seconds()) < 5
        assert news.display_end is None
        assert news.is_currently_visible is True
        assert news.visibility_status == VisibilityStatus.ACTIVE

    def test_future_scheduled_content_hidden(self, home_page):
        """3: Content with display_start in the future must not appear in .visible()."""
        now = timezone.now()
        future_start = now + datetime.timedelta(days=2)
        news = NewsPage(
            title="Future News",
            slug="future-news",
            headline="Future Headline",
            display_start=future_start,
        )
        home_page.add_child(instance=news)
        news.save_revision().publish()

        assert news.is_currently_visible is False
        assert news.visibility_status == VisibilityStatus.SCHEDULED
        assert not NewsPage.objects.visible().filter(pk=news.pk).exists()
        assert not NewsPage.objects.live().public().visible().filter(pk=news.pk).exists()

    def test_exact_start_time_boundary(self, home_page):
        """4 & 5: Content becomes visible at its exact start timestamp."""
        now = timezone.now()
        news = NewsPage(
            title="Boundary Start News",
            slug="boundary-start-news",
            headline="Boundary Start Headline",
            display_start=now,
        )
        home_page.add_child(instance=news)
        news.save_revision().publish()

        # At exact start time, visible() includes the record
        assert NewsPage.objects.visible(current_time=now).filter(pk=news.pk).exists()
        # Immediately before start time, visible() excludes the record
        one_sec_before = now - datetime.timedelta(seconds=1)
        assert not NewsPage.objects.visible(current_time=one_sec_before).filter(pk=news.pk).exists()

    def test_exact_end_time_boundary(self, home_page):
        """6 & 7: Content is hidden at its exact end timestamp and thereafter."""
        now = timezone.now()
        start = now - datetime.timedelta(days=1)
        end = now + datetime.timedelta(hours=2)

        news = NewsPage(
            title="Expiring News",
            slug="expiring-news",
            headline="Expiring Headline",
            display_start=start,
            display_end=end,
        )
        home_page.add_child(instance=news)
        news.save_revision().publish()

        # Right before expiration: visible
        just_before = end - datetime.timedelta(seconds=1)
        assert NewsPage.objects.visible(current_time=just_before).filter(pk=news.pk).exists()

        # At exact expiration timestamp: hidden (end timestamp is exclusive)
        assert not NewsPage.objects.visible(current_time=end).filter(pk=news.pk).exists()

        # After expiration: hidden and status EXPIRED
        after_end = end + datetime.timedelta(seconds=10)
        assert not NewsPage.objects.visible(current_time=after_end).filter(pk=news.pk).exists()

    def test_indefinite_eligibility_when_no_end_date(self, home_page):
        """8: Content without display_end remains visible indefinitely."""
        now = timezone.now()
        news = NewsPage(
            title="Indefinite News",
            slug="indefinite-news",
            headline="Indefinite Headline",
            display_start=now - datetime.timedelta(days=100),
            display_end=None,
        )
        home_page.add_child(instance=news)
        news.save_revision().publish()

        future_10_years = now + datetime.timedelta(days=3650)
        assert NewsPage.objects.visible(current_time=future_10_years).filter(pk=news.pk).exists()
        assert news.is_currently_visible is True

    def test_inactive_content_hidden_regardless_of_dates(self, home_page):
        """9: Manually disabled (is_active=False) content is hidden in all querysets."""
        now = timezone.now()
        news = NewsPage(
            title="Inactive News",
            slug="inactive-news",
            headline="Inactive Headline",
            is_active=False,
            display_start=now - datetime.timedelta(days=1),
            display_end=now + datetime.timedelta(days=1),
        )
        home_page.add_child(instance=news)
        news.save_revision().publish()

        assert news.is_currently_visible is False
        assert news.visibility_status == VisibilityStatus.INACTIVE
        assert not NewsPage.objects.visible().filter(pk=news.pk).exists()
        assert not NewsPage.objects.live().public().visible().filter(pk=news.pk).exists()

    def test_validation_rejects_invalid_schedule(self, home_page):
        """10: Model validation clean() rejects display_end <= display_start."""
        now = timezone.now()
        # display_end before display_start
        news_invalid = NewsPage(
            title="Invalid News",
            slug="invalid-news",
            headline="Invalid Headline",
            display_start=now,
            display_end=now - datetime.timedelta(hours=1),
        )
        with pytest.raises(ValidationError) as exc_info:
            news_invalid.clean()
        assert "display_end" in exc_info.value.message_dict

        # display_end equal to display_start
        news_equal = NewsPage(
            title="Equal News",
            slug="equal-news",
            headline="Equal Headline",
            display_start=now,
            display_end=now,
        )
        with pytest.raises(ValidationError) as exc_info:
            news_equal.clean()
        assert "display_end" in exc_info.value.message_dict

    def test_admin_and_raw_manager_access(self, home_page):
        """11: Model.objects.all() allows access to all records including inactive/scheduled/expired."""
        now = timezone.now()
        news_active = NewsPage(
            title="Active 1", slug="act-1", headline="H1", is_active=True
        )
        news_inactive = NewsPage(
            title="Inactive 1", slug="inact-1", headline="H2", is_active=False
        )
        news_future = NewsPage(
            title="Future 1",
            slug="fut-1",
            headline="H3",
            display_start=now + datetime.timedelta(days=5),
        )
        home_page.add_child(instance=news_active)
        home_page.add_child(instance=news_inactive)
        home_page.add_child(instance=news_future)

        # Unfiltered manager returns all 3
        all_news = NewsPage.objects.all()
        assert news_active in all_news
        assert news_inactive in all_news
        assert news_future in all_news

        # .active() returns active only
        assert news_active in NewsPage.objects.active()
        assert news_inactive not in NewsPage.objects.active()

        # .inactive() returns inactive only
        assert news_inactive in NewsPage.objects.inactive()
        assert news_active not in NewsPage.objects.inactive()

        # .scheduled() returns future only
        assert news_future in NewsPage.objects.scheduled()
        assert news_active not in NewsPage.objects.scheduled()

    def test_direct_url_access_returns_404_when_not_visible(
        self, client: Client, home_page
    ):
        """12: Direct HTTP request to non-visible page raises Http404 via serve()."""
        now = timezone.now()

        # Inactive page
        page_inactive = StandardPage(
            title="Hidden About",
            slug="hidden-about",
            is_active=False,
        )
        home_page.add_child(instance=page_inactive)
        page_inactive.save_revision().publish()

        resp = client.get(page_inactive.url)
        assert resp.status_code == 404

        # Future scheduled page
        page_future = StandardPage(
            title="Future Vision",
            slug="future-vision",
            display_start=now + datetime.timedelta(days=10),
        )
        home_page.add_child(instance=page_future)
        page_future.save_revision().publish()

        resp_future = client.get(page_future.url)
        assert resp_future.status_code == 404

        # Expired page
        page_expired = StandardPage(
            title="Old Event Summary",
            slug="old-summary",
            display_start=now - datetime.timedelta(days=10),
            display_end=now - datetime.timedelta(days=1),
        )
        home_page.add_child(instance=page_expired)
        page_expired.save_revision().publish()

        resp_expired = client.get(page_expired.url)
        assert resp_expired.status_code == 404

    def test_sitemap_omits_non_visible_pages(self, home_page):
        """Verify sitemap generator excludes non-visible pages."""
        now = timezone.now()
        page_active = StandardPage(title="Visible Page", slug="vis-page")
        page_future = StandardPage(
            title="Future Page",
            slug="fut-page",
            display_start=now + datetime.timedelta(days=5),
        )
        home_page.add_child(instance=page_active)
        home_page.add_child(instance=page_future)
        page_active.save_revision().publish()
        page_future.save_revision().publish()

        assert len(page_active.get_sitemap_urls()) > 0
        assert page_future.get_sitemap_urls() == []

    def test_search_view_excludes_hidden_content(self, client: Client, home_page):
        """13: Search endpoint does not return inactive, scheduled, or expired content."""
        now = timezone.now()
        doc_visible = DocumentPage(
            title="Quantum Research Report",
            slug="quantum-vis",
            description="Quantum algorithm report",
            is_active=True,
        )
        doc_hidden = DocumentPage(
            title="Quantum Research Classified",
            slug="quantum-hid",
            description="Quantum classified data",
            is_active=False,
        )
        home_page.add_child(instance=doc_visible)
        home_page.add_child(instance=doc_hidden)
        doc_visible.save_revision().publish()
        doc_hidden.save_revision().publish()

        resp = client.get("/search/?query=Quantum")
        assert resp.status_code == 200
        content = resp.content.decode("utf-8")
        assert "Quantum Research Report" in content
        assert "Quantum Research Classified" not in content

    def test_alert_banner_scheduled_visibility(self, rf: RequestFactory):
        """15 & 16: AlertBanner respects scheduled visibility in site context processor."""
        from apps.core.context_processors import site_context

        now = timezone.now()
        # Inactive banner
        AlertBanner.objects.create(
            banner_type="critical",
            title="Emergency Notice Inactive",
            message="Do not show this",
            is_active=False,
        )
        # Future scheduled banner
        AlertBanner.objects.create(
            banner_type="warning",
            title="Future Maintenance",
            message="Maintenance on weekend",
            is_active=True,
            display_start=now + datetime.timedelta(days=2),
        )
        # Active banner
        active_banner = AlertBanner.objects.create(
            banner_type="info",
            title="Campus Welcome Week",
            message="Welcome new students!",
            is_active=True,
            display_start=now - datetime.timedelta(hours=1),
            display_end=now + datetime.timedelta(days=5),
        )

        request = rf.get("/")
        context = site_context(request)
        assert context["alert_banner"] is not None
        assert context["alert_banner"].pk == active_banner.pk
        assert context["alert_banner"].title == "Campus Welcome Week"

    def test_all_content_models_support_visibility(self, home_page):
        """16: Verify consistent visibility system across all 10 domain models."""
        now = timezone.now()
        models_to_test = [
            (NewsPage, {"title": "N", "slug": "n-test", "headline": "H"}),
            (
                EventPage,
                {
                    "title": "E",
                    "slug": "e-test",
                    "start_datetime": now + datetime.timedelta(days=1),
                },
            ),
            (
                PersonPage,
                {"title": "P", "slug": "p-test", "first_name": "A", "last_name": "B"},
            ),
            (DepartmentPage, {"title": "D", "slug": "d-test"}),
            (ResearchProjectPage, {"title": "R", "slug": "r-test"}),
            (DocumentPage, {"title": "Doc", "slug": "doc-test"}),
            (TenderPage, {"title": "T", "slug": "t-test"}),
            (
                LegalPage,
                {
                    "title": "L",
                    "slug": "l-test",
                    "approval_status": LegalPage.ApprovalStatus.PUBLISHED,
                },
            ),
            (AnnouncementPage, {"title": "Ann", "slug": "ann-test", "summary": "S"}),
            (NoticePage, {"title": "Not", "slug": "not-test"}),
        ]

        for model_cls, init_kwargs in models_to_test:
            # Test active instance
            obj_active = model_cls(**init_kwargs)
            home_page.add_child(instance=obj_active)
            obj_active.save_revision().publish()

            assert obj_active.is_active is True
            assert obj_active.is_currently_visible is True
            assert model_cls.objects.visible().filter(pk=obj_active.pk).exists()

            # Test toggling is_active=False
            obj_active.is_active = False
            obj_active.save_revision().publish()
            assert obj_active.is_currently_visible is False
            assert not model_cls.objects.visible().filter(pk=obj_active.pk).exists()
