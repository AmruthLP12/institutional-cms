# Nakashara Institutional CMS

A production-oriented institutional website and content management system built with **Django 6.1.1** and **Wagtail 8.0**, managed with **uv** and styled with **Tailwind CSS v4** and **DaisyUI v5** (npm-based).

---

## 🏛️ System Overview

The Nakashara CMS is an institutional content portal designed for research institutes, universities, and public institutions. It emphasizes:

1. **Structured Content**: Strict domain models (news, research, events, faculty directory, tenders, careers, annual reports, notices) rather than unconstrained freeform canvas builders.
2. **Institutional Governance & Legal Workflows**: Distinct separation between CMS publication and statutory/institutional legal approval (`approval_status`).
3. **100% Local Static Assets**: Zero runtime CDN dependencies. HTMX, Alpine.js, SVG icons, and typography are bundled locally.
4. **Accessible Institutional Design**: Semantic HTML5, WCAG 2.2 AA target, accessible contrast ratios, keyboard navigation, and responsive layouts.
5. **Production Monolith Architecture**: Modular monolithic Django applications with PostgreSQL in production and SQLite for local development and testing.

---

## 🛠️ Technology Stack

| Component | Technology | Version | Notes |
|---|---|---|---|
| **Language** | Python | 3.14.3 | Managed via `uv` |
| **Framework** | Django | 6.1.1 | LTS release |
| **CMS Engine** | Wagtail | 8.0 | Headless-ready Wagtail |
| **Package Manager** | uv | >= 0.10 | Modern fast Python package manager |
| **CSS System** | Tailwind CSS + DaisyUI | Tailwind v4.3, DaisyUI v5.7 | Compiled via npm in `theme/` |
| **Interactivity** | HTMX & Alpine.js | HTMX 2.0.4, Alpine 3.14.8 | Fully bundled as local static files |
| **Database** | PostgreSQL / SQLite | Psycopg 3.3.6 | SQLite for dev/test; Postgres for prod |
| **Static Handling** | WhiteNoise | 6.12.0 | Cache-busted compressed static files |
| **Testing** | pytest + pytest-django | pytest 9.1 | 21 automated tests, 100% passing |
| **Linter / Formatter**| Ruff | 0.16.9 | Clean PEP 8 compliance |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.14 (or let `uv` download and manage it)
- Node.js (v20+ or v24+) and npm (for compiling Tailwind CSS)
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 2. Clone and Setup Environment
```bash
git clone <repository_url> nakashara-cms
cd nakashara-cms

# Create venv and install all dependencies via uv
uv venv
uv sync
```

### 3. Build Tailwind CSS and DaisyUI Theme
```bash
cd theme/static_src
npm install
npm run build
cd ../..
```

### 4. Apply Database Migrations
```bash
uv run python manage.py migrate
```

### 5. Setup Institutional Roles and Permission Groups
```bash
uv run python manage.py setup_groups
```
Configures standard institutional groups:
- `Administrators`
- `Content Editors`
- `Content Publishers`
- `Policy Editors`
- `Document Managers`
- `News Editors`
- `Events Editors`
- `Reviewers`

### 6. Seed Institutional Demonstration and Policy Content
The `seed_cms` command is idempotent and safe to run multiple times:
```bash
# Seed full demonstration portal (departments, news, events, research, people)
uv run python manage.py seed_cms --demo

# Seed institutional legal and policy placeholders (Privacy, Accessibility, Terms, etc.)
uv run python manage.py seed_cms --legal

# Seed navigation and quick links
uv run python manage.py seed_cms --navigation

# Or seed all sections at once:
uv run python manage.py seed_cms
```

### 7. Create Superuser and Start Development Server
```bash
uv run python manage.py createsuperuser
uv run python manage.py runserver
```
Visit:
- Public Website: [http://localhost:8000/](http://localhost:8000/)
- Wagtail CMS Admin: [http://localhost:8000/admin/](http://localhost:8000/admin/)
- Django Admin: [http://localhost:8000/django-admin/](http://localhost:8000/django-admin/)

---

## 📁 Application Architecture

```text
apps/
├── core/            # BasePage, TimeStampedModel, StreamField blocks, context processors, seed commands
├── site_settings/   # SiteSettings (identity, contacts, social), NavMenuItem, AlertBanner, FooterLinkGroup
├── home/            # HomePage (hero, statistics strip, news/events feeds, quick links, highlights)
├── content/         # StandardPage, ContactPage (form), AnnouncementPage, NoticePage
├── news/            # NewsIndexPage, NewsPage, NewsCategory snippet
├── events/          # EventIndexPage, EventPage, EventCategory snippet (upcoming vs past)
├── people/          # PersonIndexPage, PersonPage, PersonCategory snippet
├── departments/     # DepartmentIndexPage, DepartmentPage
├── research/        # ResearchIndexPage, ResearchProjectPage, ResearchArea snippet
├── documents/       # DocumentPage, PublicationPage, ReportPage, TenderPage, CareerPage
├── legal/           # LegalIndexPage, LegalPage (statutory policy metadata & approval gating)
└── search/          # PostgreSQL / Wagtail search view with live HTMX instant search
```

---

## ⚖️ Legal & Policy Workflow Governance

As mandated by institutional governance standards (`docs/legal-pages.md`):

> **Critical Rule**: CMS publication is NOT equivalent to institutional approval.

1. Each `LegalPage` carries a distinct `approval_status` (`draft`, `under_review`, `approved`, `published`, `archived`).
2. Even if an editor marks a policy page as published in the CMS, it remains hidden from public view and returns a `404 Not Found` unless its `approval_status == 'published'`.
3. Policy metadata tracks version number, approving authority, resolution reference number, effective dates, and scheduled review dates.

---

## 🧪 Testing and Verification

Run the test suite:
```bash
uv run pytest
```

Check code formatting and linting:
```bash
uv run ruff check .
uv run ruff format --check .
```

Verify production deployment configuration:
```bash
DJANGO_SETTINGS_MODULE=config.settings.production \
DJANGO_SECRET_KEY="<strong-secret-key>" \
DJANGO_ALLOWED_HOSTS="nakashara.example.org" \
DATABASE_URL="postgresql://user:pass@localhost:5432/nksr_db" \
CSRF_TRUSTED_ORIGINS="https://nakashara.example.org" \
uv run python manage.py check --deploy
```

---

## 🎨 Theme Development Workflow

To watch and recompile Tailwind CSS and DaisyUI during development:
```bash
cd theme/static_src
npm run dev
```
Or use Honcho via the provided `Procfile`:
```bash
uv run python manage.py tailwind start
```

---

## 🔒 Security and Production Deployment

- **Database**: PostgreSQL 16+ using `psycopg` binary driver.
- **Reverse Proxy**: Nginx or Apache terminating TLS, proxying to Gunicorn (`config.wsgi:application`).
- **Media Storage**: Private/restricted document collections served via `WAGTAILDOCS_SERVE_METHOD = "serve_view"`.
- **Environment**: All secrets configured through environment variables or `.env` file via `python-decouple`.

---

## 📄 License

Proprietary and Confidential — Nakashara Institutional Systems.
