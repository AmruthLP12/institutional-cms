import pytest

from apps.home.models import QuickLinkItem


@pytest.mark.django_db
class TestNavigation:
    def test_navigation_and_quicklinks(self, client, home_page):
        QuickLinkItem.objects.create(
            page=home_page,
            label="Faculty Directory",
            link_url="https://nakashara.example.org/people/",
        )

        response = client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Faculty Directory" in content
