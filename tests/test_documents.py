import datetime

import pytest
from django.utils import timezone

from apps.documents.models import (
    DocumentIndexPage,
    DocumentPage,
    TenderIndexPage,
    TenderPage,
)


@pytest.mark.django_db
class TestDocumentsApp:
    def test_document_listing(self, client, home_page):
        doc_index = DocumentIndexPage(title="Documents", slug="documents")
        home_page.add_child(instance=doc_index)
        doc_index.save_revision().publish()

        doc_page = DocumentPage(
            title="Institutional Statute Handbook",
            slug="statute-handbook",
            document_type="policy",
            publication_date=timezone.now().date(),
            is_public=True,
            description="Complete governance guidelines.",
        )
        doc_index.add_child(instance=doc_page)
        doc_page.save_revision().publish()

        # Public listing test
        res = client.get("/documents/")
        assert res.status_code == 200
        assert "Institutional Statute Handbook" in res.content.decode()

    def test_private_documents_hidden(self, client, home_page):
        """Private documents must not appear in public index listings."""
        doc_index = DocumentIndexPage(title="Documents", slug="documents")
        home_page.add_child(instance=doc_index)
        doc_index.save_revision().publish()

        doc_private = DocumentPage(
            title="Confidential Internal Audit",
            slug="internal-audit",
            document_type="report",
            publication_date=timezone.now().date(),
            is_public=False,
        )
        doc_index.add_child(instance=doc_private)
        doc_private.save_revision().publish()

        res = client.get("/documents/")
        assert res.status_code == 200
        assert "Confidential Internal Audit" not in res.content.decode()

    def test_tenders_and_careers(self, client, home_page):
        tender_index = TenderIndexPage(title="Tenders", slug="tenders")
        home_page.add_child(instance=tender_index)
        tender_index.save_revision().publish()

        tender = TenderPage(
            title="Supply of Chromatography Columns",
            slug="tender-chromatography",
            reference_number="NKSR/TEN/001",
            status="open",
            closing_date=timezone.now().date() + datetime.timedelta(days=20),
        )
        tender_index.add_child(instance=tender)
        tender.save_revision().publish()

        res_tender = client.get("/tenders/")
        assert res_tender.status_code == 200
        assert "Supply of Chromatography Columns" in res_tender.content.decode()
