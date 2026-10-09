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

    def test_hero_carousel_slides(self, client, home_page):
        from apps.home.models import HomePageHeroSlide

        HomePageHeroSlide.objects.create(
            page=home_page,
            headline="Breakthrough in Quantum Computing",
            subheadline="New quantum labs opened on campus.",
            tag="Research Excellence",
            cta_label="Read More",
            cta_url="https://nakashara.example.org/research/",
        )
        HomePageHeroSlide.objects.create(
            page=home_page,
            headline="Admissions Open for Fall 2027",
            subheadline="Join our global scholarly community.",
            tag="Admissions",
            cta_label="Apply Now",
            cta_url="https://nakashara.example.org/apply/",
        )

        response = client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Breakthrough in Quantum Computing" in content
        assert "Admissions Open for Fall 2027" in content
        assert "Institutional Highlights Carousel" in content
