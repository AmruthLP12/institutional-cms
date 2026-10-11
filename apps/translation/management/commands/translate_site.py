"""
apps/translation/management/commands/translate_site.py — CLI tool to generate or update translations.
"""

from django.core.management.base import BaseCommand
from wagtail.models import Locale, Page

from apps.translation.engine import TranslationEngine
from apps.translation.providers import get_translation_provider


class Command(BaseCommand):
    help = "Generate or refresh machine translations for pages across the CMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--language",
            type=str,
            help="Target language code (e.g. 'kn', 'hi').",
        )
        parser.add_argument(
            "--provider",
            type=str,
            default="mock",
            help="Translation provider to use ('mock', 'google').",
        )
        parser.add_argument(
            "--publish",
            action="store_true",
            help="Publish immediately instead of saving as draft revision (default: False).",
        )

    def handle(self, *args, **options):
        lang_code = options.get("language")
        provider_name = options.get("provider", "mock")
        publish = options.get("publish", False)

        provider = get_translation_provider(provider_name)
        engine = TranslationEngine(provider=provider)

        default_locale = Locale.get_default()
        source_pages = Page.objects.filter(locale=default_locale, depth__gte=2)

        if lang_code:
            target_locales = Locale.objects.filter(language_code=lang_code)
        else:
            target_locales = Locale.objects.exclude(id=default_locale.id)

        if not target_locales.exists():
            self.stderr.write(f"No target locales found matching '{lang_code}'.")
            return

        for target_locale in target_locales:
            self.stdout.write(f"Translating into {target_locale.get_display_name()}...")
            count = 0
            for page in source_pages:
                try:
                    specific_page = page.specific
                    trans = engine.translate_page(
                        specific_page,
                        target_locale,
                        provider=provider,
                        save_draft=not publish,
                    )
                    count += 1
                    self.stdout.write(f"  ✓ {specific_page.title} -> {trans.title}")
                except Exception as e:
                    self.stderr.write(f"  ✗ Failed {page.title}: {e}")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully processed {count} pages for {target_locale.get_display_name()}."
                )
            )
