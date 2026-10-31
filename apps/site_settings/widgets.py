"""
Custom Wagtail Admin Form Widgets for Site Settings.
"""

from typing import Any

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from apps.site_settings.themes import DEFAULT_THEME, THEMES, get_theme


class ThemeRadioSelect(forms.RadioSelect):
    """
    Accessible, visual radio widget for Wagtail admin theme selection.
    Renders human-readable theme names, descriptions, color swatches,
    and a live institutional component preview for each theme.
    """

    template_name = "site_settings/admin/theme_radio_select.html"

    def get_context(self, name: str, value: Any, attrs: dict[str, Any] | None) -> dict[str, Any]:
        context = super().get_context(name, value, attrs)
        active_id = str(value) if value else DEFAULT_THEME
        if active_id not in THEMES:
            active_id = DEFAULT_THEME

        context["active_theme_meta"] = get_theme(active_id)
        context["default_theme_id"] = DEFAULT_THEME

        # Enrich each choice option with theme metadata
        if "widget" in context and "optgroups" in context["widget"]:
            for _group_name, group_options, _group_index in context["widget"]["optgroups"]:
                for opt in group_options:
                    opt_val = str(opt["value"])
                    meta = THEMES.get(opt_val, get_theme(DEFAULT_THEME))
                    opt["theme_meta"] = meta
                    opt["is_currently_active"] = (opt_val == active_id)

        return context

    def render(self, name: str, value: Any, attrs: dict[str, Any] | None = None, renderer: Any = None) -> str:
        context = self.get_context(name, value, attrs)
        return mark_safe(render_to_string(self.template_name, context))

