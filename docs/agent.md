# Agent Instructions

## Role

You are the implementation agent for a production-quality institutional CMS.

Read this file and every relevant skill under `.agent/*/SKILL.md` before making substantial changes.

The project may contain skills for:

- Django development
- Django architecture
- UI/UX
- Frontend design
- SEO
- file organization
- testing
- security
- deployment

Do not assume a skill exists. Discover available skills first.

## Skill precedence

1. User's explicit request.
2. Project documentation in `docs/`.
3. Relevant `.agent/*/SKILL.md`.
4. Official documentation for the selected technology.
5. Established engineering practice.

If two skills conflict, use the more specific instruction for the current task and document important decisions.

## Mandatory current-version policy

Before adding or upgrading a dependency:

1. Check its current stable release.
2. Check maintenance status.
3. Check supported Python/Django versions.
4. Check compatibility with existing dependencies.
5. Prefer official project documentation and PyPI/package metadata.
6. Do not install an abandoned or obviously stale dependency merely because it appears in an old skill.
7. Do not upgrade a dependency blindly when the upgrade creates unnecessary compatibility risk.
8. Record significant dependency decisions.

Never copy old version numbers from examples without verification.

## Architecture rules

Use Django's built-in features before adding third-party packages.

Prefer:

- Django models
- Django forms
- Django authentication and permissions
- Django middleware
- Django templates
- Wagtail page models
- Wagtail snippets
- Wagtail StreamField
- Wagtail workflows
- Wagtail redirects
- PostgreSQL
- Django cache framework

Do not introduce:

- React
- Next.js
- Vite
- GraphQL
- Elasticsearch
- Celery
- Redis
- Channels

unless there is a concrete requirement and the dependency is justified.

## Wagtail rules

Content should be structured.

Do not create one generic page model containing arbitrary HTML for everything.

Use:

- Page models for hierarchical content.
- Snippets for reusable global content.
- Orderables for repeatable structured data.
- StreamField for flexible editorial sections.
- Documents/images through Wagtail's media system.
- Workflows for approval-sensitive content.
- Redirects for URL changes.
- Search indexing for public content.

Legal/policy pages must have explicit metadata such as:

- policy type
- version
- effective date
- last reviewed date
- next review date
- owning department
- approval status
- approving authority where applicable
- related documents

## UI rules

Use Tailwind through django-tailwind.

Do not create a frontend SPA.

Use server-rendered HTML by default.

Use DaisyUI only if installed through a compatible current Tailwind/django-tailwind workflow.

Use Lucide or another consistent SVG icon library.

Never use emoji as UI icons.

Maintain:

- visible keyboard focus
- semantic HTML
- accessible labels
- responsive layouts
- sufficient contrast
- reduced-motion support
- touch-friendly controls
- no horizontal overflow

The supplied UI/UX skill explicitly prioritizes accessibility, touch interaction, performance and responsive layout. Apply those principles rather than treating visual polish as decoration.

## Design process

For major UI work:

1. Understand the institution and audience.
2. Define a compact design system.
3. Choose typography intentionally.
4. Define spacing and layout rules.
5. Define responsive behavior.
6. Build reusable components.
7. Review accessibility.
8. Review visual consistency.
9. Remove unnecessary decorative elements.

Do not generate a generic SaaS dashboard aesthetic for a public institutional website.

## SEO rules

Use:

- semantic headings
- canonical URLs
- XML sitemap
- robots.txt
- Open Graph metadata
- appropriate structured data
- descriptive metadata
- optimized images
- meaningful alt text
- clean URLs
- breadcrumbs where useful

SEO should not override accessibility or editorial quality.

## Security

Never:

- commit secrets
- expose private media
- trust user-provided filenames
- render unsafe HTML without appropriate sanitization
- disable CSRF
- weaken Django security middleware for convenience
- expose debug mode in production

Use:

```python
DEBUG = False
```

in production.

Configure:

- HTTPS
- secure cookies
- HSTS when appropriate
- CSP where feasible
- X-Content-Type-Options
- Referrer-Policy
- clickjacking protection
- secure upload handling

Run:

```bash
python manage.py check --deploy
```

## Testing

Critical content and publishing behavior must be tested.

Test:

- page rendering
- publishing permissions
- workflow permissions
- legal page metadata
- navigation
- document access
- search
- redirects
- forms
- SEO metadata
- seed commands
- security-sensitive views

Do not claim a coverage percentage that was not actually measured.

## Database

Use PostgreSQL for production.

Use proper:

- constraints
- indexes
- relationships
- transactions
- migrations

Avoid unnecessary denormalization.

Use `select_related()` and `prefetch_related()` after identifying actual query paths.

## Git and changelog

Every meaningful change must update:

`docs/CHANGELOG.md`

Format:

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

Use the real date.

Do not invent release history.

## Working method

Before changing code:

1. Inspect the repository.
2. Read relevant documentation.
3. Read relevant skills.
4. Identify existing conventions.
5. Make the smallest coherent change.
6. Run relevant tests/checks.
7. Update documentation.
8. Update changelog.

After implementation:

```bash
python manage.py check
python manage.py test
```

and any project-specific checks.

## Communication

When a task is ambiguous, state the assumption before implementation.

When a dependency is questionable, verify it rather than guessing.

When a legal requirement is institution-specific, create an editable placeholder and clearly mark it for institutional/legal review.

Never fabricate institutional policies, statutory claims, officer names, registration numbers or regulatory approvals.
