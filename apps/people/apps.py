"""
People app — AppConfig for the Nakashara institutional directory.
"""

from django.apps import AppConfig


class PeopleConfig(AppConfig):
    name = "apps.people"
    label = "people"
    verbose_name = "People"

    def ready(self) -> None:
        """Import signal handlers once the app registry is fully populated."""
        pass  # Reserved for future signal wiring.
