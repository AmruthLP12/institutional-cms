"""
apps/translation/providers/__init__.py — Provider registry and factory.
"""

from django.conf import settings

from apps.translation.providers.base import BaseTranslationProvider
from apps.translation.providers.google import GoogleCloudTranslationProvider
from apps.translation.providers.mock import MockTranslationProvider

PROVIDERS: dict[str, type[BaseTranslationProvider]] = {
    "mock": MockTranslationProvider,
    "google": GoogleCloudTranslationProvider,
}


def get_translation_provider(name: str | None = None) -> BaseTranslationProvider:
    """
    Get configured translation provider instance.
    """
    provider_name = name or getattr(settings, "TRANSLATION_DEFAULT_PROVIDER", "mock")
    provider_cls = PROVIDERS.get(provider_name.lower(), MockTranslationProvider)
    return provider_cls()
