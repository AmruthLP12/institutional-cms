"""
Centralized Theme Definitions — Nakashara Institutional CMS

Defines the five calm, accessible, WCAG 2.2 AA compliant institutional color themes:
1. Academic Blue (default) — Traditional Oxford Navy, Muted Steel & Antique Gold
2. Sage & Ivory — Calm Academic Forest, Muted Sage & Warm Sand
3. Slate & Steel — Contemporary Intellectual Slate, Cool Steel & Warm Bronze
4. Burgundy & Cream — Distinguished Deep Wine, Rose Muted & Burnished Ochre
5. Teal & Stone — Refined Deep Sea Teal, Muted Verdigris & Soft Ochre
"""

from typing import Any

DEFAULT_THEME = "academic-blue"

THEMES: dict[str, dict[str, Any]] = {
    "academic-blue": {
        "id": "academic-blue",
        "name": "Academic Blue",
        "label": "Academic Blue (Default)",
        "description": "Dignified Oxford Navy with Muted Steel Blue secondary and warm Antique Gold accents. Designed for timeless academic excellence, scholarship, and public trust.",
        "colors": {
            "primary": "#17365D",
            "primary_hover": "#0F243E",
            "primary_fg": "#FFFFFF",
            "secondary": "#52749A",
            "secondary_hover": "#3D5A7A",
            "secondary_fg": "#FFFFFF",
            "accent": "#D6A75D",
            "accent_hover": "#C29348",
            "accent_fg": "#172635",
            "page_bg": "#F7F8FA",
            "surface": "#FFFFFF",
            "surface_secondary": "#EEF2F6",
            "surface_elevated": "#FFFFFF",
            "text_main": "#202C3A",
            "text_secondary": "#364558",
            "text_muted": "#566579",
            "text_heading": "#17365D",
            "link": "#17365D",
            "link_hover": "#52749A",
            "border_default": "#E2E8F0",
            "border_strong": "#CBD5E1",
            "divider": "#EDF2F7",
            "focus_ring": "#17365D",
            "hover_bg": "#F1F5F9",
            "selected_bg": "#E2E8F0",
            "header_bg": "#FFFFFF",
            "footer_bg": "#0E1B2D",
            "footer_text": "#CBD5E1",
            "footer_border": "#D6A75D",
            "success": "#1E6B43",
            "success_fg": "#FFFFFF",
            "warning": "#92400E",
            "warning_fg": "#FFFFFF",
            "error": "#991B1B",
            "error_fg": "#FFFFFF",
            "info": "#1D4ED8",
            "info_fg": "#FFFFFF",
        },
    },
    "sage-ivory": {
        "id": "sage-ivory",
        "name": "Sage & Ivory",
        "label": "Sage & Ivory",
        "description": "Restrained academic forest green with gentle sage and warm sand accents over an ivory canvas. Ideal for environmental sciences, humanities, and sustained reading.",
        "colors": {
            "primary": "#344B40",
            "primary_hover": "#23342C",
            "primary_fg": "#FFFFFF",
            "secondary": "#718878",
            "secondary_hover": "#556B5C",
            "secondary_fg": "#FFFFFF",
            "accent": "#C6AD7A",
            "accent_hover": "#B39761",
            "accent_fg": "#202A24",
            "page_bg": "#F5F6F0",
            "surface": "#FFFFFF",
            "surface_secondary": "#EAECE2",
            "surface_elevated": "#FFFFFF",
            "text_main": "#28342D",
            "text_secondary": "#3D4F45",
            "text_muted": "#5C6F64",
            "text_heading": "#344B40",
            "link": "#344B40",
            "link_hover": "#718878",
            "border_default": "#E1E5DC",
            "border_strong": "#C8D0C2",
            "divider": "#ECEFE8",
            "focus_ring": "#344B40",
            "hover_bg": "#ECEFE8",
            "selected_bg": "#DFE4D8",
            "header_bg": "#FFFFFF",
            "footer_bg": "#15221B",
            "footer_text": "#CBD5CF",
            "footer_border": "#C6AD7A",
            "success": "#1E6B43",
            "success_fg": "#FFFFFF",
            "warning": "#92400E",
            "warning_fg": "#FFFFFF",
            "error": "#991B1B",
            "error_fg": "#FFFFFF",
            "info": "#1D4ED8",
            "info_fg": "#FFFFFF",
        },
    },
    "slate-steel": {
        "id": "slate-steel",
        "name": "Slate & Steel",
        "label": "Slate & Steel",
        "description": "Cool slate gray and architectural steel blue paired with burnished bronze accents. Ideal for engineering, modern research laboratories, and policy institutes.",
        "colors": {
            "primary": "#334155",
            "primary_hover": "#1E293B",
            "primary_fg": "#FFFFFF",
            "secondary": "#647C91",
            "secondary_hover": "#4D6377",
            "secondary_fg": "#FFFFFF",
            "accent": "#B68D58",
            "accent_hover": "#A17743",
            "accent_fg": "#18222E",
            "page_bg": "#F3F5F7",
            "surface": "#FFFFFF",
            "surface_secondary": "#E7ECF0",
            "surface_elevated": "#FFFFFF",
            "text_main": "#273444",
            "text_secondary": "#3C4E61",
            "text_muted": "#596A7C",
            "text_heading": "#334155",
            "link": "#334155",
            "link_hover": "#647C91",
            "border_default": "#E2E8F0",
            "border_strong": "#CBD5E1",
            "divider": "#EDF1F5",
            "focus_ring": "#334155",
            "hover_bg": "#EAEFF4",
            "selected_bg": "#DFE5EB",
            "header_bg": "#FFFFFF",
            "footer_bg": "#16202C",
            "footer_text": "#CCD5DE",
            "footer_border": "#B68D58",
            "success": "#1E6B43",
            "success_fg": "#FFFFFF",
            "warning": "#92400E",
            "warning_fg": "#FFFFFF",
            "error": "#991B1B",
            "error_fg": "#FFFFFF",
            "info": "#1D4ED8",
            "info_fg": "#FFFFFF",
        },
    },
    "burgundy-cream": {
        "id": "burgundy-cream",
        "name": "Burgundy & Cream",
        "label": "Burgundy & Cream",
        "description": "Distinguished deep burgundy with muted dusty rose and warm ochre accents over warm cream canvas. Designed for historical institutions, law faculties, and university archives.",
        "colors": {
            "primary": "#633B43",
            "primary_hover": "#47292F",
            "primary_fg": "#FFFFFF",
            "secondary": "#987078",
            "secondary_hover": "#7E565E",
            "secondary_fg": "#FFFFFF",
            "accent": "#B99A66",
            "accent_hover": "#A3834F",
            "accent_fg": "#261C1E",
            "page_bg": "#FAF7F2",
            "surface": "#FFFFFF",
            "surface_secondary": "#F2EAE0",
            "surface_elevated": "#FFFFFF",
            "text_main": "#382D30",
            "text_secondary": "#524045",
            "text_muted": "#735D63",
            "text_heading": "#633B43",
            "link": "#633B43",
            "link_hover": "#987078",
            "border_default": "#EBE2D8",
            "border_strong": "#D7CABE",
            "divider": "#F4ECE3",
            "focus_ring": "#633B43",
            "hover_bg": "#F4ECE3",
            "selected_bg": "#E8DDD2",
            "header_bg": "#FFFFFF",
            "footer_bg": "#221417",
            "footer_text": "#D8CFD1",
            "footer_border": "#B99A66",
            "success": "#1E6B43",
            "success_fg": "#FFFFFF",
            "warning": "#92400E",
            "warning_fg": "#FFFFFF",
            "error": "#991B1B",
            "error_fg": "#FFFFFF",
            "info": "#1D4ED8",
            "info_fg": "#FFFFFF",
        },
    },
    "teal-stone": {
        "id": "teal-stone",
        "name": "Teal & Stone",
        "label": "Teal & Stone",
        "description": "Deep ocean teal with muted verdigris and soft antique bronze on a cool stone canvas. Ideal for biomedical research, interdisciplinary faculties, and maritime sciences.",
        "colors": {
            "primary": "#244B4B",
            "primary_hover": "#163232",
            "primary_fg": "#FFFFFF",
            "secondary": "#588481",
            "secondary_hover": "#426B68",
            "secondary_fg": "#FFFFFF",
            "accent": "#C5A46A",
            "accent_hover": "#AF8E53",
            "accent_fg": "#182525",
            "page_bg": "#F5F7F6",
            "surface": "#FFFFFF",
            "surface_secondary": "#E7ECEB",
            "surface_elevated": "#FFFFFF",
            "text_main": "#293838",
            "text_secondary": "#3E5252",
            "text_muted": "#587070",
            "text_heading": "#244B4B",
            "link": "#244B4B",
            "link_hover": "#588481",
            "border_default": "#E0E7E6",
            "border_strong": "#C6D4D2",
            "divider": "#EDF3F2",
            "focus_ring": "#244B4B",
            "hover_bg": "#EBF0EF",
            "selected_bg": "#DCE4E3",
            "header_bg": "#FFFFFF",
            "footer_bg": "#112323",
            "footer_text": "#CDD7D6",
            "footer_border": "#C5A46A",
            "success": "#1E6B43",
            "success_fg": "#FFFFFF",
            "warning": "#92400E",
            "warning_fg": "#FFFFFF",
            "error": "#991B1B",
            "error_fg": "#FFFFFF",
            "info": "#1D4ED8",
            "info_fg": "#FFFFFF",
        },
    },
}

VALID_THEMES = set(THEMES.keys())

THEME_CHOICES = [
    (theme_id, f"{meta['name']} — {meta['description']}")
    for theme_id, meta in THEMES.items()
]


def get_theme(theme_id: str | None) -> dict[str, Any]:
    """
    Return theme metadata for the given identifier.
    Falls back safely to DEFAULT_THEME ('academic-blue') if identifier is invalid or missing.
    """
    if theme_id and theme_id in THEMES:
        return THEMES[theme_id]
    return THEMES[DEFAULT_THEME]


def get_active_theme_identifier(theme_id: str | None) -> str:
    """
    Validate and return a safe theme identifier.
    """
    if theme_id and theme_id in THEMES:
        return theme_id
    return DEFAULT_THEME

