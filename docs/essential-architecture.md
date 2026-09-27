# Essential Architecture

This document contains the architecture that should not be casually changed.

## 1. Application type

A server-rendered institutional website and CMS.

Primary CMS:

**Wagtail**

Primary framework:

**Django**

Primary database:

**PostgreSQL**

## 2. Target stack

```text
Python 3.14.x
Django 6.1.x
Wagtail 8.x
django-tailwind 4.x
Tailwind CSS 4.x
PostgreSQL
Django templates
StreamField
HTMX (only when justified)
DaisyUI (optional and compatibility-checked)
Lucide icons or equivalent SVG icon set
pytest / pytest-django
Ruff
```

The exact patch releases must be resolved at installation time.

## 3. Rendering model

Default:

```text
Request
  -> Django URL
  -> Wagtail page/view
  -> Django template
  -> Tailwind CSS
  -> HTML response
```

Do not create a React/Next.js frontend unless the requirements change.

## 4. CMS model

### Page content

Use Wagtail `Page` subclasses.

Examples:

```text
HomePage
StandardPage
NewsIndexPage
NewsPage
EventIndexPage
EventPage
DepartmentIndexPage
DepartmentPage
PersonIndexPage
PersonPage
ResearchIndexPage
ResearchProjectPage
DocumentIndexPage
LegalIndexPage
LegalPage
ContactPage
```

The final model names may differ if a better domain model is discovered.

### Reusable content

Use Wagtail snippets for:

- Site settings
- Navigation items where appropriate
- Contact information
- Social links
- Footer links
- Alerts
- Departments
- Categories
- Authors
- Policy owners

## 5. StreamField

Use controlled blocks rather than unrestricted HTML.

Potential blocks:

```text
Heading
Paragraph
RichText
Image
Quote
CallToAction
LinkList
CardGrid
Statistics
DocumentList
Notice
Alert
Accordion
Timeline
Gallery
Embed
ContactDetails
```

Only add blocks that are actually required.

## 6. Legal content

Legal and policy pages are first-class CMS content.

They should be public pages but editable only by authorized users.

Metadata:

```text
title
slug
policy_type
version
effective_from
last_reviewed_at
next_review_at
owner_department
approval_status
approved_by
summary
content
related_documents
contact_information
```

Approval status:

```text
Draft
Under Review
Approved
Published
Archived
```

Do not treat a normal page publication as equivalent to legal approval.

## 7. Permissions

Define groups such as:

```text
Administrators
Content Editors
Content Publishers
Legal/Policy Editors
Document Managers
News Editors
Events Editors
Reviewers
```

Exact permissions must be implemented using Wagtail/Django permissions and workflows.

## 8. Public website information architecture

Minimum page families:

```text
Home
About
Leadership
Departments
Research
Academics
People
News
Events
Announcements
Notices
Careers
Tenders
Publications
Reports
Documents
Contact
Legal & Policies
Accessibility
Privacy
Copyright
Disclaimer
```

The exact information architecture must remain configurable.

## 9. Media

Use Wagtail media/document functionality.

Requirements:

- alt text
- captions where relevant
- meaningful filenames
- safe upload validation
- controlled private/public collections
- document metadata
- replacement/version workflow where needed

## 10. Search

Start with database-backed search suitable for the expected scale.

Use PostgreSQL search features where appropriate.

Do not add Elasticsearch merely because it is available.

## 11. SEO

Every public page should support:

```text
title
meta description
canonical URL
social image
robots behavior
```

Generate:

- sitemap.xml
- robots.txt
- canonical URLs
- Open Graph metadata

Use structured data where appropriate.

## 12. Accessibility

Target WCAG 2.2 AA as the design goal.

Required:

- keyboard navigation
- visible focus
- semantic landmarks
- accessible forms
- meaningful link text
- alt text
- sufficient contrast
- responsive text
- reduced motion
- screen-reader-friendly states

## 13. Integration boundary

Keep CMS content separate from transactional applications.

Example:

```text
Institutional Platform
|
+-- CMS
|    +-- Public pages
|    +-- News
|    +-- Events
|    +-- Documents
|    +-- Policies
|
+-- ERP
|    +-- Payroll
|    +-- Leave
|    +-- Procurement
|    +-- Inventory
|
+-- Identity
|    +-- LDAP/OIDC/etc.
|
+-- Research systems
```

Integrations must have explicit contracts.

## 14. No unnecessary complexity

Do not introduce:

- microservices
- message brokers
- Kubernetes
- GraphQL
- SPA frontend
- Elasticsearch
- Redis
- Celery

until a measurable requirement exists.

Start as a modular Django monolith.

## 15. Documentation rule

Architecture decisions that affect:

- database
- authentication
- CMS model
- deployment
- dependencies
- integrations

must be reflected in `docs/architecture.md`.
