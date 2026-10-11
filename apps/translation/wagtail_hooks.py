"""
apps/translation/wagtail_hooks.py — Wagtail admin hooks for translation workflows and reporting.
"""

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin import messages
from wagtail.admin.widgets.button import ListingButton
from wagtail.models import Locale, Page

from apps.translation.engine import TranslationEngine
from apps.translation.models import TranslationRecord, TranslationWorkflowStatus


@hooks.register("register_page_listing_more_buttons")
def add_translate_page_button(page, user, next_url=None):
    """
    Add a button to page listings permitting quick machine-translation into configured target languages.
    """
    if not page.is_root():
        # Look up locales other than the page's current locale
        target_locales = Locale.objects.exclude(id=page.locale_id)
        for loc in target_locales:
            url = reverse("translate_page", args=[page.id, loc.language_code])
            yield ListingButton(
                f"Translate ({loc.language_code.upper()})",
                url,
                priority=60,
                attrs={"title": f"Create machine-translated draft in {loc.get_display_name()}"},
            )


def translate_page_admin_view(request, page_id, lang_code):
    """
    Admin view handling one-click translation request for a page into lang_code.
    """
    page = get_object_or_404(Page, id=page_id).specific
    target_locale = get_object_or_404(Locale, language_code=lang_code)

    engine = TranslationEngine()
    try:
        translated_page = engine.translate_page(page, target_locale, save_draft=True)
        messages.success(
            request,
            f"Draft translation created for '{translated_page.title}' in {target_locale.get_display_name()}. It is saved as an unreviewed draft.",
        )
        return HttpResponseRedirect(reverse("wagtailadmin_pages:edit", args=[translated_page.id]))
    except Exception as e:
        messages.error(request, f"Translation failed: {e}")
        return HttpResponseRedirect(reverse("wagtailadmin_explore", args=[page.get_parent().id]))


@hooks.register("register_admin_urls")
def register_translation_admin_urls():
    return [
        path(
            "pages/<int:page_id>/translate/<str:lang_code>/",
            translate_page_admin_view,
            name="translate_page",
        ),
    ]
