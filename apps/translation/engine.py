"""
apps/translation/engine.py — Core translation engine for page trees and StreamFields.
"""

import copy
import logging
from django.utils import timezone
from wagtail.models import Locale, Page

from apps.translation.models import (
    TranslationRecord,
    TranslationWorkflowStatus,
)
from apps.translation.providers import get_translation_provider
from apps.translation.providers.base import BaseTranslationProvider

logger = logging.getLogger(__name__)


class TranslationEngine:
    """
    Engine orchestrating translation creation and synchronization across Wagtail page trees.
    """

    def __init__(self, provider: BaseTranslationProvider | None = None):
        self.provider = provider or get_translation_provider()

    def translate_page(
        self,
        source_page: Page,
        target_locale: Locale,
        provider: BaseTranslationProvider | None = None,
        save_draft: bool = True,
    ) -> Page:
        """
        Creates or updates a translated counterpart of source_page in target_locale.
        Ensures proper StreamField block handling, slug generation, and TranslationRecord tracking.
        """
        active_provider = provider or self.provider
        target_lang = target_locale.language_code
        source_lang = source_page.locale.language_code

        # If translation already exists, retrieve it; otherwise use copy_for_translation
        translated_page = source_page.get_translation_or_none(target_locale)
        is_new = False

        if translated_page is None:
            is_new = True
            # Clone structure to target locale
            translated_page = source_page.copy_for_translation(
                target_locale,
                copy_parents=True,
                alias=False,
            )

        # Translate scalar fields
        translated_title = active_provider.translate_text(
            source_page.title, target_lang, source_language=source_lang
        )
        translated_page.title = translated_title

        # Preserve a URL-safe slug
        translated_page.slug = f"{source_page.slug}-{target_lang}" if is_new else translated_page.slug

        if hasattr(source_page, "meta_description") and source_page.meta_description:
            translated_page.meta_description = active_provider.translate_text(
                source_page.meta_description, target_lang, source_language=source_lang
            )

        if hasattr(source_page, "intro") and source_page.intro:
            # Check if intro is RichText
            is_rich = hasattr(source_page.intro, "source")
            intro_text = source_page.intro.source if is_rich else str(source_page.intro)
            translated_intro = active_provider.translate_text(
                intro_text, target_lang, source_language=source_lang, is_html=is_rich
            )
            translated_page.intro = translated_intro

        # Translate StreamField if present
        if hasattr(source_page, "body") and source_page.body is not None:
            translated_page.body = self.translate_stream_field(
                source_page.body, target_lang, source_language=source_lang, provider=active_provider
            )

        # Save as draft (never publish directly to ensure editorial review)
        if save_draft:
            translated_page.live = False
            translated_page.has_unpublished_changes = True
            translated_page.save_revision()
        else:
            translated_page.save()

        # Update or create TranslationRecord
        content_hash = TranslationRecord.calculate_content_hash(source_page)
        record, _ = TranslationRecord.objects.get_or_create(
            translated_page=translated_page,
            defaults={
                "source_page": source_page,
                "status": TranslationWorkflowStatus.DRAFT,
                "provider_used": active_provider.name,
                "source_content_hash": content_hash,
                "last_translated_at": timezone.now(),
            },
        )
        record.source_page = source_page
        record.provider_used = active_provider.name
        record.source_content_hash = content_hash
        record.last_translated_at = timezone.now()
        record.save()

        return translated_page

    def translate_stream_field(
        self,
        stream_value,
        target_lang: str,
        source_language: str = "en",
        provider: BaseTranslationProvider | None = None,
    ):
        """
        Recursively translates translatable block fields in a StreamField while preserving
        non-textual attributes (images, documents, choices, IDs, and block hierarchy).
        """
        active_provider = provider or self.provider
        raw_data = copy.deepcopy(stream_value.raw_data)

        for block in raw_data:
            block_type = block.get("type")
            value = block.get("value")
            if not value:
                continue

            if block_type == "heading" and isinstance(value, dict):
                if "text" in value:
                    value["text"] = active_provider.translate_text(
                        value["text"], target_lang, source_language=source_language
                    )

            elif block_type == "rich_text":
                if isinstance(value, str):
                    block["value"] = active_provider.translate_text(
                        value, target_lang, source_language=source_language, is_html=True
                    )

            elif block_type == "quote" and isinstance(value, dict):
                if "text" in value:
                    value["text"] = active_provider.translate_text(
                        value["text"], target_lang, source_language=source_language
                    )
                if "attribution" in value and value["attribution"]:
                    value["attribution"] = active_provider.translate_text(
                        value["attribution"], target_lang, source_language=source_language
                    )
                if "attribution_title" in value and value["attribution_title"]:
                    value["attribution_title"] = active_provider.translate_text(
                        value["attribution_title"], target_lang, source_language=source_language
                    )

            elif block_type == "call_to_action" and isinstance(value, dict):
                if "title" in value:
                    value["title"] = active_provider.translate_text(
                        value["title"], target_lang, source_language=source_language
                    )
                if "text" in value and value["text"]:
                    value["text"] = active_provider.translate_text(
                        value["text"], target_lang, source_language=source_language
                    )
                if "button_label" in value:
                    value["button_label"] = active_provider.translate_text(
                        value["button_label"], target_lang, source_language=source_language
                    )

            elif block_type == "notice" and isinstance(value, dict):
                if "title" in value and value["title"]:
                    value["title"] = active_provider.translate_text(
                        value["title"], target_lang, source_language=source_language
                    )
                if "text" in value and value["text"]:
                    value["text"] = active_provider.translate_text(
                        value["text"], target_lang, source_language=source_language, is_html=True
                    )

            elif block_type == "accordion" and isinstance(value, dict):
                if "title" in value and value["title"]:
                    value["title"] = active_provider.translate_text(
                        value["title"], target_lang, source_language=source_language
                    )
                if "items" in value and isinstance(value["items"], list):
                    for item in value["items"]:
                        if isinstance(item, dict):
                            if "question" in item:
                                item["question"] = active_provider.translate_text(
                                    item["question"], target_lang, source_language=source_language
                                )
                            if "answer" in item:
                                item["answer"] = active_provider.translate_text(
                                    item["answer"], target_lang, source_language=source_language, is_html=True
                                )

            elif block_type == "statistics" and isinstance(value, dict):
                if "title" in value and value["title"]:
                    value["title"] = active_provider.translate_text(
                        value["title"], target_lang, source_language=source_language
                    )
                if "items" in value and isinstance(value["items"], list):
                    for item in value["items"]:
                        if isinstance(item, dict):
                            if "label" in item:
                                item["label"] = active_provider.translate_text(
                                    item["label"], target_lang, source_language=source_language
                                )
                            if "description" in item and item["description"]:
                                item["description"] = active_provider.translate_text(
                                    item["description"], target_lang, source_language=source_language
                                )

        # Construct a new StreamValue of the same StreamBlock type
        stream_block = stream_value.stream_block
        return stream_block.to_python(raw_data)
