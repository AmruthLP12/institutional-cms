"""Core app configuration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "Core"

    def ready(self):
        pass  # Import signals here if needed in the future
