"""Documents app configuration."""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    name = "apps.documents"
    label = "documents"
    verbose_name = "Documents & Publications"

    def ready(self):
        pass  # Import signals here if needed in the future
