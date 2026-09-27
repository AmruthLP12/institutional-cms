# Master Project Generation Prompt

Copy the following prompt into your coding agent.

---

You are building a production-oriented institutional website and CMS.

The project is a **Django + Wagtail modular monolith** intended for an institution such as a research institute, university, public institution or similar organization.

## First: inspect the repository

Before changing anything:

1. Inspect the repository tree.
2. Read `README.md`.
3. Read every relevant file in `docs/`.
4. Discover every skill under `.agent/*/SKILL.md`.
5. Read the relevant skills before implementing their domain.
6. Do not assume that a pasted skill's package versions are current.
7. Check current stable releases and compatibility using official documentation/PyPI.

The `.agent` directory is expected to contain skills such as:

```text
.agent/
├── django-developer/
│   └── SKILL.md
├── django-pro/
│   └── SKILL.md
├── frontend-design/
│   └── SKILL.md
├── senior-architect/
│   └── SKILL.md
├── senior-fullstack/
│   └── SKILL.md
├── ui-ux-pro-max/
│   └── SKILL.md
├── seo-optimizer/
│   └── SKILL.md
└── ...
```

Use only the skills actually present.

## Technology requirements

Use the current stable ecosystem.

Target:

- Python current stable 3.14.x
- Django current stable 6.1.x
- Wagtail current stable 8.x
- django-tailwind current maintained 4.x release
- Tailwind CSS 4.x
- PostgreSQL
- Django templates
- Wagtail StreamField
- pytest / pytest-django
- Ruff

The exact patch versions must be checked before installation.

If the current stable versions change between this prompt and execution, use the then-current stable compatible versions instead.

Do not use obsolete Django 4.x/5.x examples simply because a skill contains them.

Do not use pre-release Python/Django/Wagtail versions in production.

## Tailwind requirement

Use:

https://django-tailwind.readthedocs.io/en/latest/installation.html

Do NOT introduce Vite.

Do NOT create a separate React/Next.js frontend.

Use django-tailwind's supported installation and management commands.

If DaisyUI is used, verify that the current DaisyUI release is compatible with the selected Tailwind and django-tailwind setup.

DaisyUI is optional, not mandatory.

Use Lucide or another maintained SVG icon library.

Never use emoji as interface icons.

## Architectural requirement

Use a modular Django monolith.

```text
Institutional Website
        |
        v
Django
        |
        +-- Wagtail CMS
        |
        +-- Public website
        |
        +-- Institutional modules
        |
        v
PostgreSQL
```

Do not introduce microservices.

Do not introduce React.

Do not introduce Next.js.

Do not introduce Vite.

Do not introduce GraphQL.

Do not introduce Elasticsearch.

Do not introduce Redis.

Do not introduce Celery.

Do not introduce Channels.

unless a real requirement is identified and documented.

Start simple.

## CMS requirement

Use Wagtail as the primary CMS.

Build structured page types for:

- Home
- About
- Leadership
- Departments
- Academics
- Research
- People
- News
- Events
- Announcements
- Notices
- Careers
- Tenders
- Publications
- Reports
- Documents
- Contact
- Legal & Policies

Use StreamField for controlled page composition.

Do not create a generic HTML page builder where editors can destroy the site's information architecture.

## CMS-managed legal and policy content

This is mandatory.

Create a dedicated legal/policy content model or page family.

It must support CMS management of:

- Privacy Policy
- Accessibility Statement
- Copyright
- Disclaimer
- Terms of Use
- Cookie Policy where applicable
- Website Usage Policy
- Security contact
- Institutional policies
- Research policies
- Information security policies
- Public-information pages
- RTI/public-information content where applicable
- Grievance information where applicable
- Procurement/tender public information
- Other institution-approved policy pages

Do not assume that every institution legally requires every page.

Make the legal section configurable.

Legal/policy pages must support:

```text
Policy type
Version
Status
Effective date
Last reviewed date
Next review date
Owner department
Approving authority
Approval reference
Approval date
Summary
Body
Related documents
Contact information
```

Statuses:

```text
Draft
Under Review
Approved
Published
Archived
```

Policy/legal content must support an approval workflow separate from ordinary editorial publishing.

Do not represent CMS publication as legal approval.

Seed only obvious placeholder content.

Never fabricate legal claims, statutory references, government notifications, officer names or compliance statements.

## Public website pages

Generate all necessary public templates and routes.

At minimum:

```text
/
 /about/
/leadership/
/departments/
/research/
/people/
/academics/
/news/
/events/
/announcements/
/notices/
/careers/
/tenders/
/publications/
/reports/
/documents/
/contact/
/policies/
/privacy/
/accessibility/
/copyright/
/disclaimer/
/terms/
```

Do not hard-code these URLs if Wagtail's page hierarchy can provide them cleanly.

## Homepage

Create a complete institutional homepage with:

- institutional identity
- hero/intro
- announcements
- featured news
- upcoming events
- research highlights
- important links
- documents/notices
- contact/footer
- legal links

Do not make it look like a generic SaaS landing page.

The design should feel appropriate for an established academic/research/public institution.

## UI/UX

Before implementing major UI work:

1. Read the available UI/UX skill.
2. Read the frontend-design skill.
3. If the UI/UX skill includes a design-system search script, use it.
4. Define typography, colors, spacing, layout and interaction rules.
5. Review the design against the institutional context.
6. Implement responsive HTML.

Use:

- semantic HTML
- accessible forms
- visible focus
- keyboard navigation
- SVG icons
- accessible contrast
- responsive layouts
- reduced motion
- 44px+ touch targets where appropriate
- no horizontal scrolling

Avoid:

- generic SaaS cards everywhere
- excessive gradients
- excessive rounded containers
- unnecessary animation
- emoji icons
- decorative labels with no information value
- template-looking hero sections

## SEO

Read the available SEO skill.

Implement:

- page title
- meta description
- canonical URL
- Open Graph metadata
- social image
- robots control
- sitemap.xml
- robots.txt
- breadcrumbs where useful
- structured data where appropriate
- clean URLs
- descriptive alt text

Do not add an SEO package without checking whether Django/Wagtail plus a small internal implementation is sufficient.

## Accessibility

Target WCAG 2.2 AA as the design target.

Test:

- keyboard navigation
- focus states
- screen-reader labels
- form labels
- heading hierarchy
- contrast
- responsive behavior
- reduced motion

## Search

Start with Wagtail/PostgreSQL-backed search.

Search should cover public:

- pages
- news
- events
- documents
- departments
- people
- research

Never expose private content through search.

Do not install Elasticsearch unless performance requirements justify it.

## Media

Use Wagtail images/documents.

Support:

- alt text
- captions
- document metadata
- public/private distinction
- safe upload handling

Private documents must never be exposed through public URLs.

## Authentication and permissions

Use Django/Wagtail permissions.

Create sensible groups such as:

```text
Administrators
Content Editors
Content Publishers
Policy Editors
Document Managers
Reviewers
```

Use Wagtail workflows for approval-sensitive content.

Do not create a second custom permission framework unless necessary.

## Database

Use PostgreSQL in production.

Use:

- foreign keys
- constraints
- indexes
- transactions
- proper migrations

Optimize actual query paths with:

- select_related
- prefetch_related

Do not prematurely optimize.

## Testing

Use pytest/pytest-django where appropriate.

Test:

- models
- pages
- page rendering
- publishing
- workflows
- permissions
- legal content
- search
- navigation
- seed commands
- SEO metadata
- forms
- redirects
- private documents

Run:

```bash
python manage.py check
python manage.py check --deploy
python manage.py test
pytest
```

Do not claim coverage percentages unless measured.

## Seed data

Create idempotent management commands.

At minimum:

```bash
python manage.py seed_cms --demo
python manage.py seed_cms --legal
python manage.py seed_cms --navigation
```

or one command with equivalent options.

Repeated execution must not create duplicates.

Seed:

- homepage
- navigation
- about
- departments
- sample news
- sample events
- sample documents metadata
- legal placeholders

Mark demo/legal content as placeholder.

## Project files

Create:

```text
README.md

docs/
├── agent.md
├── essential-architecture.md
├── architecture.md
├── prod.md
├── content-model.md
├── legal-pages.md
├── CHANGELOG.md
└── project-generation-prompt.md
```

All documentation must live under `docs/`, except the root `README.md`.

## README

Write a full README containing:

- project purpose
- features
- architecture
- technology stack
- prerequisites
- installation
- environment setup
- database setup
- Tailwind setup
- seed commands
- test commands
- lint commands
- Wagtail admin usage
- development workflow
- production deployment overview
- security
- backup
- maintenance
- troubleshooting
- documentation links

## Changelog

Create `docs/CHANGELOG.md`.

Use exactly this style:

```markdown
## [0.3.0] - 2026-09-26

### Added

- ...

### Changed

- ...

### Fixed

- ...

### Removed

- ...
```

For every release:

- use a real semantic version
- use the actual date
- list all relevant Added items
- list all relevant Changed items
- list all relevant Fixed items
- list all relevant Removed items

Never silently change the changelog.

## Dependency policy

Before installing each non-standard dependency:

1. Check PyPI/npm/GitHub/official documentation.
2. Check latest stable release.
3. Check release date.
4. Check maintenance activity.
5. Check supported Python/Django/Tailwind versions.
6. Check security status.
7. Prefer actively maintained projects.
8. Prefer Django/Wagtail built-ins where possible.

Document important decisions.

Do not install a package just because a skill recommends it.

## Package installation

Use the simplest package management strategy supported by the environment.

If the repository already uses `uv`, preserve it.

Otherwise a normal virtual environment plus pinned requirements is acceptable.

Do not introduce multiple package managers unnecessarily.

## Production

The deployment guide must explain:

- environment variables
- PostgreSQL
- migrations
- collectstatic
- Tailwind build
- Wagtail
- Apache/reverse proxy
- application server
- media
- backups
- HTTPS
- security checks
- monitoring
- rollback

If the environment uses Apache, do not replace it with nginx.

## Security

Run:

```bash
python manage.py check --deploy
```

Production must use:

```text
DEBUG=False
secure cookies
HTTPS
restricted ALLOWED_HOSTS
safe CSRF configuration
security headers
protected private media
secret management
```

## Legal caution

The project is a CMS implementation.

It is not a source of legal advice.

Where legal content is required, build the CMS capability and placeholder content, and clearly require institutional/legal review before publication.

## Final verification

Before declaring the project complete:

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py test
pytest
ruff check .
ruff format --check .
```

Also manually verify:

```text
Homepage
Navigation
News
Events
Documents
Search
Legal pages
Accessibility
Mobile layout
Wagtail admin
Publishing workflow
Seed command
Sitemap
robots.txt
404 page
500 page
```

Then update:

```text
README.md
docs/CHANGELOG.md
```

Do not claim completion until the checks that are applicable to the implemented project have actually passed.

---
