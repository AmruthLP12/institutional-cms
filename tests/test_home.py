import pytest


@pytest.mark.django_db
class TestHomePage:
    def test_home_page_rendering(self, client, home_page):
        response = client.get("/")
        assert response.status_code == 200
        assert "Nakashara" in response.content.decode()

    def test_hero_section_present(self, client, home_page):
        response = client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Pioneering Research" in content

    def test_home_page_context(self, client, home_page):
        response = client.get("/")
        assert "featured_news" in response.context
        assert "upcoming_events" in response.context
        assert "announcements" in response.context
        assert "notices" in response.context
