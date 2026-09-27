import pytest
from django.utils import timezone

from apps.news.models import NewsCategory, NewsIndexPage, NewsPage


@pytest.mark.django_db
class TestNewsApp:
    def test_news_listing_and_filtering(self, client, home_page):
        news_index = NewsIndexPage(title="News & Media", slug="news")
        home_page.add_child(instance=news_index)
        news_index.save_revision().publish()

        cat1, _ = NewsCategory.objects.get_or_create(name="Research", slug="research")
        cat2, _ = NewsCategory.objects.get_or_create(name="Campus", slug="campus")

        article1 = NewsPage(
            title="Quantum Computing Center Opened",
            slug="quantum-center",
            headline="New Facility Inaugurated",
            summary="New state of the art lab.",
            publication_date=timezone.now().date(),
        )
        news_index.add_child(instance=article1)
        article1.categories.add(cat1)
        article1.save_revision().publish()

        article2 = NewsPage(
            title="Campus Green Initiative",
            slug="campus-green",
            headline="Solar Array Operational",
            summary="Zero carbon campus target.",
            publication_date=timezone.now().date(),
        )
        news_index.add_child(instance=article2)
        article2.categories.add(cat2)
        article2.save_revision().publish()

        # Listing test
        response = client.get("/news/")
        assert response.status_code == 200
        assert "New Facility Inaugurated" in response.content.decode()
        assert "Solar Array Operational" in response.content.decode()

        # Category filter test
        res_filter = client.get("/news/?category=research")
        assert res_filter.status_code == 200
        content = res_filter.content.decode()
        assert "New Facility Inaugurated" in content

        # Detail view test
        res_detail = client.get("/news/quantum-center/")
        assert res_detail.status_code == 200
        assert "New Facility Inaugurated" in res_detail.content.decode()
