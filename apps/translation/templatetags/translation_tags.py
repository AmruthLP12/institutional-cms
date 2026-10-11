"""
apps/translation/templatetags/translation_tags.py — Template tags for language selector and hreflang.
"""

from django import template
from django.utils.translation import get_language
from wagtail.models import Locale, Page

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_languages(context):
    """
    Returns available languages configured on the site.
    """
    from apps.translation.models import ManagedLanguage

    managed = ManagedLanguage.objects.filter(is_enabled=True).select_related("locale").order_by("sort_order")
    if managed.exists():
        return [
            {
                "code": m.locale.language_code,
                "name": m.native_name,
                "is_default": m.is_default,
                "is_rtl": m.is_rtl,
            }
            for m in managed
        ]

    # Fallback to DB Locales
    locales = Locale.objects.all()
    results = []
    names = {
        "en": "English",
        "kn": "ಕನ್ನಡ",
        "hi": "हिन्दी",
    }
    for loc in locales:
        results.append(
            {
                "code": loc.language_code,
                "name": names.get(loc.language_code, loc.get_display_name()),
                "is_default": loc.language_code == "en",
                "is_rtl": False,
            }
        )
    return results


@register.simple_tag(takes_context=True)
def page_alternate_url(context, lang_code: str):
    """
    Returns the URL of the current page in the specified language code,
    or falls back to the homepage in that language or language prefix.
    """
    page = context.get("page")
    request = context.get("request")

    if isinstance(page, Page):
        try:
            target_locale = Locale.objects.get(language_code=lang_code)
            translated = page.get_translation_or_none(target_locale)
            if translated and translated.live:
                return translated.get_url(request=request)
        except Exception:
            pass

    # Fallback to language prefixed URL if available
    if request:
        return f"/{lang_code}/"

    return f"/{lang_code}/"


@register.simple_tag(takes_context=True)
def get_hreflang_tags(context):
    """
    Generates a list of hreflang alternate links for the current page.
    """
    page = context.get("page")
    request = context.get("request")
    if not isinstance(page, Page):
        return []

    tags = []
    try:
        translations = page.get_translations().live()
        # Add current page
        tags.append({
            "lang": page.locale.language_code,
            "url": page.get_full_url(request=request) or page.get_url(request=request),
        })
        for trans in translations:
            tags.append({
                "lang": trans.locale.language_code,
                "url": trans.get_full_url(request=request) or trans.get_url(request=request),
            })
    except Exception:
        pass

    return tags
