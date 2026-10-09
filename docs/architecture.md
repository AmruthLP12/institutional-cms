# System Architecture

## 1. Architectural style

The project uses a **modular Django monolith**.

This is intentional.

The institutional website and CMS have strong domain relationships, and a single deployable application reduces operational complexity.

```text
                         Internet
                            |
                            v
                    Apache / TLS
                            |
                            v
                  Django / Wagtail
                    /           \
                   /             \
              Public UI        CMS Admin
                   |               |
                   +-------+-------+
                           |
                       Domain Apps
                           |
                     PostgreSQL
```

## 2. Suggested project structure

```text
project/
├── manage.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── core/
│   ├── home/
│   ├── content/
│   ├── news/
│   ├── events/
│   ├── people/
│   ├── departments/
│   ├── research/
│   ├── documents/
│   ├── legal/
│   ├── search/
│   └── site_settings/
│
├── theme/
├── templates/
├── static/
├── media/
├── tests/
├── fixtures/
├── scripts/
├── docs/
└── .agent/
```

Keep the number of apps reasonable. Do not create an app for every model.

## 3. Domain boundaries

### Core

Cross-cutting functionality:

- common utilities
- base models
- health checks
- shared context
- audit-related helpers

### Home/content

Public page composition.

### News

News articles and categories.

### Events

Events, schedules and locations.

### People

Public profiles.

### Departments

Organizational units.

### Research

Research groups, projects, publications and related documents.

### Documents

Institutional downloadable material.

### Legal

Policies and public legal/administrative information.

### Site settings

Global institutional configuration via `SiteSettings` (`apps.site_settings.models.SiteSettings` / `InstitutionSettings`):

- **Identity & Branding**: `institution_name`, `institution_short_name`, `tagline`, `logo`, `logo_alt_text`, `favicon`
- **General Contact**: `phone_primary`, `phone_secondary`, `phone_toll_free`, `fax_number`, `email_general`, `email_admissions`, `email_media`, `email_reception`, `email_accessibility`
- **Structured Postal Address**: `building_or_campus`, `address_line_1`, `address_line_2`, `city`, `state`, `postal_code`, `country`
- **Operations & Visitor Guidance**: `office_hours`, `directions_info`, `directions_url`
- **Social Media**: `twitter_url`, `linkedin_url`, `youtube_url`, `facebook_url`, `instagram_url`
- **Footer & Legal**: `footer_description`, `footer_copyright_text`, `footer_note`
- **Theme & Appearance**: `theme`, `custom_primary_color`, `custom_accent_color`
- **Analytics**: `google_analytics_id`

**Reusable Partials (`templates/includes/`)**:
- `institutional_address.html`: Schema.org `PostalAddress` microdata-enabled address block.
- `contact_details.html`: Structured telephone, email, visiting hours, and direction links with `tel:` and `mailto:` protocols.
- `social_links.html`: Accessible social media icon links omitting unconfigured platforms.
- `footer.html`: Modular 4-column institutional footer partial.

## 4. Content Visibility and Scheduling System

All institutional content models (including all `BasePage` subclasses and `AlertBanner`) inherit from `ScheduledVisibilityModel` (`apps.core.models.ScheduledVisibilityModel`).

### Central Visibility Rule

Content is eligible for public display if and only if:

```python
is_active = True
AND display_start <= timezone.now()
AND (display_end IS NULL OR display_end > timezone.now())
```

- **`is_active`** (BooleanField, default `True`): Allows administrators to manually enable or disable content.
- **`display_start`** (DateTimeField, default `timezone.now`): Timestamp from which content becomes eligible for display.
- **`display_end`** (DateTimeField, optional `null=True`, `blank=True`): Timestamp after which content automatically expires (exclusive).

### QuerySet API

- `Model.objects.visible()` / `Model.objects.filter_visible()`: Filters currently eligible public content at runtime query execution.
- `Model.objects.active()`: Returns records where `is_active=True`.
- `Model.objects.inactive()`: Returns records where `is_active=False`.
- `Model.objects.scheduled()`: Returns records scheduled for future display (`display_start > now`).
- `Model.objects.expired()`: Returns records whose `display_end` has passed (`display_end <= now`).
- `Model.objects.all()`: Full unfiltered administrative access.

### Protection & Integration

- **Direct URL Access**: `BasePage.serve(request)` raises `Http404` when `not self.is_currently_visible`.
- **Sitemaps**: `BasePage.get_sitemap_urls()` returns `[]` when `not self.is_currently_visible`.
- **Search**: `apps.search.views.search` filters search results to omit non-visible pages.
- **Wagtail Revisions & Workflows**: Independent of Wagtail publication states; scheduled visibility acts as an additional runtime eligibility condition.

## 5. Wagtail content architecture

Use Wagtail page hierarchy.

Example:

```text
Root
└── Institution
    ├── About
    ├── Academics
    ├── Research
    ├── Departments
    ├── People
    ├── News
    ├── Events
    ├── Careers
    ├── Documents
    ├── Notices
    ├── Policies
    └── Contact
```

Editors should understand the tree without developer assistance.

## 5. StreamField strategy

StreamField is for flexible editorial composition, not for replacing database models.

Example:

```python
body = StreamField(
    [
        ("rich_text", RichTextBlock()),
        ("image", ImageBlock()),
        ("quote", QuoteBlock()),
        ("document_list", DocumentListBlock()),
        ("call_to_action", CallToActionBlock()),
    ],
    use_json_field=True,
)
```

Use reusable blocks where repeated design patterns exist.

## 6. Navigation

Do not hard-code the entire navigation in templates.

Use a mixture of:

- Wagtail page hierarchy
- site settings
- controlled navigation snippets

Menus must remain editable.

## 7. Legal/policy architecture

A legal page is not just a StandardPage.

Example:

```text
LegalPage
├── title
├── policy_type
├── version
├── status
├── effective_from
├── last_reviewed_at
├── next_review_at
├── owner_department
├── approval_reference
├── summary
├── body
└── related_documents
```

The approval reference may be a document/reference number supplied by the institution.

## 8. Editorial workflow

Recommended:

```text
Editor
  |
  v
Draft
  |
  v
Reviewer
  |
  v
Approved
  |
  v
Publisher
  |
  v
Published
```

For ordinary news content, a lighter workflow may be sufficient.

For policies/legal content, approval should be mandatory.

## 9. Search architecture

Phase 1:

```text
PostgreSQL
  |
  +-- indexed fields
  +-- full-text search
  +-- Wagtail search integration
```

Phase 2 only if justified:

```text
PostgreSQL -> external search service
```

Measure first.

## 10. Caching

Start with Django's cache framework.

Potential cache targets:

- homepage fragments
- navigation
- global settings
- expensive listing pages

Do not cache personalized or permission-sensitive content incorrectly.

## 11. Background work

Use synchronous Django operations unless work is genuinely long-running.

Potential future background jobs:

- bulk document processing
- email notifications
- search indexing
- scheduled reports

Only then evaluate Celery or another maintained task system.

## 12. Authentication

For local development:

- Django user accounts.

For production:

- institutional identity integration if required.

Potential integrations:

- LDAP
- OIDC
- SAML

Do not implement an identity protocol until the institution's actual identity provider is known.

## 13. Security model

Apply defense in depth:

```text
HTTPS
 |
Django SecurityMiddleware
 |
Authentication
 |
Authorization
 |
Wagtail permissions
 |
Workflow approval
 |
Model validation
 |
Safe templates
 |
Database constraints
```

## 14. Observability

At minimum:

- structured application logs
- request/error logs
- deployment health check
- database backup monitoring
- failed task/error visibility if background tasks are added

Sentry or another monitoring service may be added if approved and actively maintained.

## 15. API

Do not build an API simply because the project could have one.

If another application needs CMS content:

- expose a deliberately scoped API
- define public/private boundaries
- authenticate private endpoints
- rate-limit where appropriate
- document the contract

Wagtail's API capabilities may be used where they meet the requirement.

## 16. Deployment

Target a conventional Linux deployment.

```text
Internet
  |
Apache
  |
Gunicorn/ASGI server as appropriate
  |
Django/Wagtail
  |
PostgreSQL
```

Use the server architecture required by the host environment.

Do not force containers if the institution's deployment environment does not need them.

## 17. Static/media

Static:

```text
python manage.py collectstatic
```

Media:

- separate persistent storage
- backups
- controlled permissions
- production-safe serving

Private documents must never be exposed through predictable public URLs.

## 18. Architectural decision record

Important decisions should be recorded in this document or a future `docs/adr/` directory.

Use:

```text
Decision
Context
Options considered
Decision
Consequences
```
