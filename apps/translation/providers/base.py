"""
apps/translation/providers/base.py — Abstract translation provider interface.
"""

from abc import ABC, abstractmethod


class BaseTranslationProvider(ABC):
    """
    Abstract translation provider.
    Subclasses implement machine translation using external APIs or local engines.
    """

    name = "base"

    @abstractmethod
    def translate_text(
        self, text: str, target_language: str, source_language: str = "en", is_html: bool = False
    ) -> str:
        """
        Translate a single string of text or HTML to target_language.
        """
        raise NotImplementedError

    def translate_batch(
        self,
        texts: list[str],
        target_language: str,
        source_language: str = "en",
        is_html: bool = False,
    ) -> list[str]:
        """
        Batch translation fallback if API doesn't support batch calls natively.
        """
        return [
            self.translate_text(
                t, target_language, source_language=source_language, is_html=is_html
            )
            for t in texts
        ]
