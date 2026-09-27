"""Events app configuration."""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    name = "apps.events"
    label = "events"
    verbose_name = "Events"

    def ready(self):
        pass  # Import signals here if needed in the future
