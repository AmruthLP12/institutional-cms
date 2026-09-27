# Changelog

All notable changes to the **Nakashara Institutional Website & Content Management System** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - 2026-09-27

### Added
- **Global Theme & Palette Switcher**:
  - Added `theme`, `custom_primary_color`, and `custom_accent_color` fields to Wagtail `SiteSettings` with options:
    - `corporate` (Clean Modern Blue & Slate — default)
    - `emerald` (Academic Deep Green & Mint)
    - `nord` (Modern Arctic Slate & Frost)
    - `winter` (Crisp Professional Cyan & Ice)
    - `business` (High-Contrast Corporate Dark)
    - `night` (Deep Modern Dark)
    - `autumn` (Warm Rust, Bronze & Cream)
    - `luxury` (Dark Gold & Deep Obsidian)
    - `light` (Default Clean Bright)
  - Configured `@plugin "daisyui" { themes: all; }` in Tailwind v4 theme source.
  - Dynamic `data-theme` and inline CSS custom property overrides on `<html data-theme="{{ site_settings.theme }}">`.
- **Contact Page (`/contact/`)**:
  - Created `ContactPage` (`apps.content.models.ContactPage`) in CMS seeder with dynamic `ContactFormField`s (Full Name, Email Address, Subject/Department, Message).
  - Seeded contact information, institutional address, and support emails.
- **Developer Tooling**:
  - Added `djlint` to `dependency-groups.dev` with custom Wagtail/Django lint configuration in `pyproject.toml`.
  - Added `django-browser-reload` to dependencies and wired middleware/URLs for instantaneous browser refresh on template edits.
- **Test Suite Expansion**:
  - Created `tests/test_htmx_and_theme.py` testing HTMX partial responses, theme selection, ContactPage rendering/submission, and QuickLinkItem internal foreign keys. (Total tests: 27/27 passing).
- **Theme & Styling Guide Documentation**:
  - Authored comprehensive developer guide in `docs/theming.md` covering the DaisyUI v5 / Tailwind CSS v4 theming architecture, Wagtail `SiteSettings` integration, root `data-theme` and inline CSS variable injection, and step-by-step procedures for adding, removing, or customizing themes.

### Changed
- **HTMX Partial Swapping across Index Pages**:
  - Implemented `get_template()` on `NewsIndexPage` returning `"news/partials/news_grid.html"` for HTMX requests, preventing full document shell nesting.
  - Implemented `get_template()` on `EventIndexPage` returning `"events/_event_list_partial.html"` for tab switching and pagination.
  - Implemented `get_template()` on `PersonIndexPage` returning `"people/partials/people_grid.html"`.
- **Homepage Quick Links Seeder**:
  - Replaced hardcoded external URLs in `QuickLinkItem` with direct `link_page` foreign keys referencing actual Wagtail `Page` objects across all 14 institutional models.
  - Pre-seeded `NavMenuItem` and `FooterLinkGroup` with internal page references.
- **Template Color Modernization**:
  - Eliminated all hardcoded hex color classes (`#1A2B4A` navy, `#C8963E` gold, and `amber-*`) across all 50 templates.
  - Replaced with DaisyUI semantic tokens (`primary`, `secondary`, `accent`, `base-100`, `base-200`, `base-300`, `base-content`).

### Fixed
- **Department Cards Hover Swapping Bug**:
  - Removed accidental `hx-get="{{ dept.url }}" hx-trigger="mouseenter once"` on `<article>` cards in `templates/departments/department_index_page.html` that caused full department pages to inject inside card tiles on mouse hover.
- **Django Test Client Context Recursion**:
  - Inlined `person_card` in `templates/people/partials/people_grid.html` to eliminate deep nested template context recursion during test instrumentation.

---

## [1.0.0] - 2026-09-27

### Added
- Initial release of Nakashara Institutional CMS built with Django 6.1.1 and Wagtail 8.0 modular monolith architecture.
- Modular apps: `core`, `site_settings`, `home`, `content`, `news`, `events`, `people`, `departments`, `research`, `documents`, `legal`, `search`.
- 100% offline static assets: HTMX 2.0.4, Alpine.js 3.14.8, local Google fonts.
- Tailwind CSS v4 + DaisyUI v5 compiled via npm.
- Two-tier statutory governance for `LegalPage` enforcing `approval_status == 'published'`.
- Idempotent management commands: `setup_groups` and `seed_cms`.
