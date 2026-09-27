# Content Model

## Principle

Use structured content where the institution has structured information.

Use flexible StreamField blocks where editors need page composition.

Do not use StreamField as a substitute for relational data.

## Core page types

### HomePage

Purpose:

- institutional identity
- featured content
- announcements
- key links
- research highlights
- upcoming events

Potential blocks:

```text
Hero
AnnouncementList
FeaturedNews
FeaturedEvents
Statistics
ResearchHighlights
QuickLinks
CallToAction
```

### StandardPage

For general institutional content.

Fields:

```text
title
intro
body
seo
```

### NewsIndexPage / NewsPage

News:

```text
headline
summary
body
featured_image
author
publication_date
categories
related_documents
```

### EventIndexPage / EventPage

Event:

```text
title
summary
description
start_datetime
end_datetime
location
registration_url
contact
image
```

### DepartmentPage

Department:

```text
name
short_name
description
contact
location
website
head
related_people
documents
```

### PersonPage

Public profile:

```text
name
designation
department
profile_photo
biography
education
research_interests
publications
email
phone
office
```

Only publish personal data approved for public display.

### ResearchProjectPage

```text
title
summary
description
principal_investigator
department
funding_information
start_date
end_date
status
publications
documents
```

Do not expose sensitive internal research information.

### DocumentPage

Metadata:

```text
title
description
document_type
publication_date
department
version
language
document
```

## Global snippets

Potential snippets:

```text
SiteSettings
ContactDetails
SocialLink
FooterLink
AlertBanner
Department
NewsCategory
EventCategory
```

## SEO model

Reusable SEO fields:

```text
seo_title
meta_description
og_image
canonical_url
no_index
```

Avoid installing a large SEO package unless the project has a demonstrated need.

## Navigation

Navigation should support:

```text
label
page/link
open_in_new_tab
children
visibility
```

Prefer Wagtail page relationships when navigation follows the page tree.

## Documents

Document metadata should include:

```text
title
description
category
publication_date
version
language
file
```

If the document is public, ensure the storage path is public-safe.

## Search indexing

Index:

- title
- intro
- body
- categories
- document metadata
- department
- people
- research projects

Do not index private fields.

## Content lifecycle

```text
Draft
  |
Review
  |
Approved
  |
Published
  |
Archived
```

Not every content type requires every stage.

## Editorial permissions

Examples:

```text
Content Editor
News Editor
Events Editor
Document Manager
Policy Editor
Reviewer
Publisher
Administrator
```

Use Wagtail's permission and workflow mechanisms rather than inventing a parallel permission system.

## Data ownership

Every major content domain should have an identifiable owner.

Example:

```text
News        -> Communications
Events      -> Events/Administration
Departments -> Administration
Policies    -> Policy Owner
Research    -> Research Office
Careers     -> HR
Tenders     -> Procurement
```

These are examples only.
