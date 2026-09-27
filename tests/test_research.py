import pytest
from django.utils import timezone

from apps.research.models import ResearchArea, ResearchIndexPage, ResearchProjectPage


@pytest.mark.django_db
class TestResearchApp:
    def test_research_project_listing_and_detail(self, client, home_page):
        res_index = ResearchIndexPage(title="Research", slug="research")
        home_page.add_child(instance=res_index)
        res_index.save_revision().publish()

        area, _ = ResearchArea.objects.get_or_create(
            name="Microbiology", slug="microbiology"
        )

        project = ResearchProjectPage(
            title="Antimicrobial Resistance Mechanisms",
            slug="amr-mechanisms",
            summary="Investigating novel resistance pathways in bacterial pathogens.",
            principal_investigator="Dr. Ananya Sen",
            status="ongoing",
            start_date=timezone.now().date(),
            funding_agency="ICMR (Demo)",
            funding_amount="INR 80 Lakhs",
        )
        res_index.add_child(instance=project)
        project.areas.add(area)
        project.save_revision().publish()

        # Listing
        res_list = client.get("/research/")
        assert res_list.status_code == 200
        assert "Antimicrobial Resistance Mechanisms" in res_list.content.decode()

        # Detail
        res_detail = client.get("/research/amr-mechanisms/")
        assert res_detail.status_code == 200
        content = res_detail.content.decode()
        assert "Antimicrobial Resistance Mechanisms" in content
        assert "Dr. Ananya Sen" in content
