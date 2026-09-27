import datetime

import pytest
from django.utils import timezone

from apps.events.models import EventIndexPage, EventPage


@pytest.mark.django_db
class TestEventsApp:
    def test_events_upcoming_and_past(self, client, home_page):
        event_index = EventIndexPage(title="Events", slug="events")
        home_page.add_child(instance=event_index)
        event_index.save_revision().publish()

        now = timezone.now()

        # Upcoming event
        ev_future = EventPage(
            title="Symposium on AI Ethics",
            slug="ai-ethics-symposium",
            summary="Future event discussing ethics.",
            start_datetime=now + datetime.timedelta(days=10),
            location_name="Auditorium A",
        )
        event_index.add_child(instance=ev_future)
        ev_future.save_revision().publish()

        # Past event
        ev_past = EventPage(
            title="Annual Convocation 2025",
            slug="convocation-2025",
            summary="Past graduation ceremony.",
            start_datetime=now - datetime.timedelta(days=60),
            location_name="Main Grounds",
        )
        event_index.add_child(instance=ev_past)
        ev_past.save_revision().publish()

        # Listing test (upcoming by default)
        response = client.get("/events/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Symposium on AI Ethics" in content

        # Detail test
        res_detail = client.get("/events/ai-ethics-symposium/")
        assert res_detail.status_code == 200
        assert "Auditorium A" in res_detail.content.decode()
