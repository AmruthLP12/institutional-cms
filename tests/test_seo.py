import pytest

from apps.content.models import StandardPage


@pytest.mark.django_db
class TestSEO:
    def test_meta_tags_and_robots(self, client, home_page):
        page = StandardPage(
            title="Admissions Overview",
            slug="admissions",
            meta_description="Guide to graduate and doctoral admissions at Nakashara.",
        )
        home_page.add_child(instance=page)
        page.save_revision().publish()

        response = client.get("/admissions/")
        assert response.status_code == 200
        content = response.content.decode()
        assert (
            'name="description" content="Guide to graduate and doctoral admissions at Nakashara."'
            in content
        )
        assert 'name="robots" content="index, follow"' in content

    def test_robots_txt(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert "Disallow: /admin/" in response.content.decode()

    def test_sitemap_xml(self, client, home_page):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        assert "<urlset" in response.content.decode()
