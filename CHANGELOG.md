# Changelog

All notable changes to the **Nakashara Institutional Website & Content Management System** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased] - 2026-10-09

### Added
- **Centralized Institutional Contact Information & Site Settings Architecture**:
  - Enriched Wagtail `SiteSettings` (`apps.site_settings.models.SiteSettings` / `InstitutionSettings`) with comprehensive institutional fields:
    - Structured Postal Address: `building_or_campus`, `address_line_1`, `address_line_2`, `city`, `state`, `postal_code`, `country`.
    - Extended Contact Lines: `phone_primary`, `phone_secondary`, `phone_toll_free`, `fax_number`.
    - Departmental Inboxes: `email_general`, `email_admissions`, `email_media`, `email_reception`, `email_accessibility`.
    - Operations & Visiting: `office_hours`, `directions_info`, `directions_url`.
    - Footer & Legal: `footer_description`, `footer_copyright_text`, `footer_note`.
  - Added helper properties: `formatted_address` (single-line comma-delimited omitting blanks), `address_lines` (structured list of non-empty lines), `has_address`, `has_contact_info`, `has_social_links`, and `social_links_list`.
  - Created reusable, accessible template partials:
    - `templates/includes/institutional_address.html`: Microdata `PostalAddress` rendering with zero broken empty lines.
    - `templates/includes/contact_details.html`: Structured contact details with accessible `tel:` and `mailto:` links, hours, and direction maps.
    - `templates/includes/social_links.html`: Official social links omitting unconfigured platforms.
    - `templates/includes/footer.html`: Modular 4-column institutional footer partial.
  - Injected `institution_settings` alongside `site_settings` in `apps.core.context_processors.site_context` for seamless template access.
  - Added test suite `tests/test_institution_settings.py` covering model registration, address formatting, social link parsing, context injection, footer rendering, contact page integration, and multi-site isolation (37/37 tests passing).
- **Complete Institutional UI/UX Overhaul**:
  - Implemented authoritative, accessible academic design system across all 50 Django templates.
  - Defined 50-900 tonal color scale in `theme/static_src/src/styles.css` with semantic color tokens: Oxford Navy (`#24466B`), Academic Sage (`#52766F`), Antique Gold (`#B58A48`), Crisp White (`#FFFFFF`), Warm Off-White (`#F5F4EF`), Soft Gray-Green (`#E2E4E1`), and Charcoal Slate (`#202B36`).
  - Added server-side hex color regex validator `^#(?:[0-9a-fA-F]{3}){1,2}$` for `SiteSettings.custom_primary_color` and `custom_accent_color`.
  - Multi-image Hero Carousel in `templates/home/home_page.html` with Alpine.js controls, keyboard navigation, auto-advance, and high-legibility dark gradient scrim overlay.
  - Full print stylesheet rules (`@media print`) and WCAG 2.2 AA compliant contrast ratios across light and dark modes.
  - Schema.org microdata `BreadcrumbList` integration in global `templates/base.html` breadcrumbs.

### Changed
- **Typography & Component Restraint**:
  - Replaced SaaS-style gradients, neon accents, and heavy pill radius overload with restrained `rounded-xl` / `rounded-lg` cards, crisp 1px borders (`border-base-300`), and subtle focus rings.
  - Standardized display headings to Source Serif 4 (`font-serif`) with tight tracking and body text to legible grotesk sans-serif (`font-sans`).
  - Redesigned all StreamField blocks (`templates/blocks/`): `cta_block`, `statistics_block`, `accordion_block`, `document_list_block`, `notice_block`, `quote_block`, `heading_block`, `image_block`, `embed_block`.
  - Redesigned all document, research, content, and legal templates: `career_index_page`, `career_page`, `document_index_page`, `document_page`, `publication_index_page`, `publication_page`, `report_index_page`, `report_page`, `tender_index_page`, `tender_page`, `contact_page`, `contact_page_landing`, `standard_page`, `announcement_index_page`, `announcement_page`, `notice_index_page`, `notice_page`, `research_index_page`, `research_project_page`, `legal_index_page`, `legal_page`, `department_index_page`, `department_page`.
  - Upgraded search templates (`search.html`, `search_results.html`) with clean search input, live HTMX debounced querying, and clear count summaries.

### Fixed
- **Text Selection & Contrast Bug**:
  - Replaced low-contrast selection class with high-contrast amber/neutral selection (`selection:bg-amber-300 selection:text-slate-950` and global `::selection` CSS rule).
- **Duplicate Breadcrumbs**:
  - Removed duplicate `<nav aria-label="Breadcrumb">` bars from interior templates; centralized breadcrumbs into `base.html`'s single, accessible breadcrumbs block.
- **Department Page Header Contrast**:
  - Fixed white text against light background in `templates/departments/department_page.html`.

---

## [Unreleased] - 2026-09-28

### Added
- **Fully Dynamic Navigation Bar**:
  - `base.html` navbar now renders from `NavMenuItem` CMS records (managed in Wagtail Admin → Snippets → Navigation menu items).
  - Desktop dropdown menus for nav items with child entries (Alpine.js animated panel, `rounded-2xl`, shadow).
  - Mobile hamburger menu with animated open/close icon, smooth `x-transition` enter/leave, and child item indentation.
  - Active-page highlight indicator (bottom border accent on the current page link).
- **Fully Dynamic Footer**:
  - Footer link columns now render from `FooterLinkGroup` Snippets (Wagtail Admin → Snippets → Footer link groups).
  - Static fallback columns shown only when no groups are configured yet.
  - Social media icon buttons with hover animation (rounded square pill, `hover:bg-secondary`).
  - Contact address, phone, and email injected from `SiteSettings`.
- **Custom 404 & 500 Error Pages (always rendered)**:
  - Added `apps/core/views.py` with `custom_404` and `custom_500` views that use `render()` instead of Django's default, ensuring branded templates render even when `DEBUG=True`.
  - Registered `handler404` and `handler500` in `config/urls.py`.
  - Added `/test-404/` and `/test-500/` dev-only routes for preview without toggling `DEBUG`.
  - Redesigned `templates/404.html` and `templates/500.html` with decorative large number, icon card, search bar, and action buttons.
- **Design System Upgrade**:
  - Added `@layer components` overrides in `theme/static_src/src/styles.css`:
    - `.btn` — `rounded-xl`, `shadow-md hover:shadow-lg`, subtle lift on hover (`translateY(-1px)`).
    - `.card` — `rounded-2xl`, `shadow-sm hover:shadow-md`.
    - `.badge` — fully pill-shaped (`rounded-full`), bolder weight.
    - `.input`, `.select`, `.textarea` — `rounded-xl` with focus ring.
    - `.modal-box` — `rounded-xl` with deep shadow.
  - Added `.card-lift` utility class for interactive card hover lift effect.
  - Added `.section-rule` utility — secondary-colored pill divider for section headings.
  - Added `.richtext` component styles for prose content (headings, links, lists, blockquote).

### Changed
- **Context Processor** (`apps/core/context_processors.py`):
  - Now injects `footer_groups` (ordered `FooterLinkGroup` with prefetched `links__page`).
  - Filters nav items by `is_visible=True` in the query.
  - Graceful degradation extended to `footer_groups = []`.
- **Breadcrumbs** in `base.html` now use SVG chevron separators instead of plain `/` characters.
- **Utility Bar** tagline now hidden on small screens (only `sm:block`) to reduce mobile clutter.
### Fixed
- **VS Code CSS Diagnostic Warning**:
  - Moved dynamic color custom property declarations from inline `style=""` on the `<html>` tag to a scoped `<style>` block in `<head>`, preventing editor CSS linting false-positives.
- **Tailwind CLI Script Compatibility**:
  - Added `"start": "npx @tailwindcss/cli -i ./src/styles.css -o ../static/css/dist/styles.css --watch"` script to `theme/static_src/package.json` so `uv run python manage.py tailwind start` runs as expected.
- **Custom Error Route Ordering**:
  - Moved `test-404/` and `test-500/` preview routes before Wagtail's catch-all `path("", include(wagtail_urls))` in `config/urls.py`, allowing direct browser testing of branded 404/500 templates in development.

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
