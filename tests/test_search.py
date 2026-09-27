import pytest

from apps.content.models import StandardPage


@pytest.mark.django_db
class TestSearchApp:
    def test_search_view_returns_results(self, client, home_page):
        page1 = StandardPage(
            title="Computational Physics Laboratory",
            slug="comp-phys",
            intro="<p>Advanced numerical simulation and computational physics.</p>",
        )
        home_page.add_child(instance=page1)
        page1.save_revision().publish()

        response = client.get("/search/?query=Computational")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Computational Physics Laboratory" in content

    def test_search_htmx_partial_response(self, client, home_page):
        response = client.get("/search/?query=Physics", HTTP_HX_REQUEST="true")
        assert response.status_code == 200
        # Partial should not include full <html> tag
        assert "<!DOCTYPE html>" not in response.content.decode()
