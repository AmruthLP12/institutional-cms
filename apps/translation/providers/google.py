"""
apps/translation/providers/google.py — Google Cloud Translation provider.
"""

import json
import logging
import urllib.parse
import urllib.request
from django.conf import settings

from apps.translation.providers.base import BaseTranslationProvider

logger = logging.getLogger(__name__)


class GoogleCloudTranslationProvider(BaseTranslationProvider):
    """
    Provider utilizing Google Cloud Translation REST API.
    Can use GOOGLE_TRANSLATE_API_KEY from settings or environment.
    Falls back gracefully to MockTranslationProvider if API key is not configured or in case of network errors.
    """

    name = "google"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or getattr(settings, "GOOGLE_TRANSLATE_API_KEY", "")

    def translate_text(
        self, text: str, target_language: str, source_language: str = "en", is_html: bool = False
    ) -> str:
        if not text or not text.strip():
            return text

        if not self.api_key:
            logger.warning(
                "GOOGLE_TRANSLATE_API_KEY not configured. Falling back to mock translation."
            )
            from apps.translation.providers.mock import MockTranslationProvider

            return MockTranslationProvider().translate_text(
                text, target_language, source_language, is_html=is_html
            )

        endpoint = f"https://translation.googleapis.com/language/translate/v2?key={self.api_key}"
        payload = {
            "q": text,
            "target": target_language,
            "source": source_language,
            "format": "html" if is_html else "text",
        }

        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                translations = result.get("data", {}).get("translations", [])
                if translations:
                    return translations[0].get("translatedText", text)
        except Exception as e:
            logger.error(f"Google Cloud Translation error: {e}. Falling back to original text.")
            return text

        return text
