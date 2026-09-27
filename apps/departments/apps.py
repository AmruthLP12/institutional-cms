"""Departments app configuration."""

from django.apps import AppConfig


class DepartmentsConfig(AppConfig):
    name = "apps.departments"
    label = "departments"
    verbose_name = "Departments"

    def ready(self):
        pass  # Import signals here if needed in the future
