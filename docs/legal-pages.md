# CMS-Managed Legal, Policy and Public-Information Content

## Purpose

Institutional websites commonly contain policy and legal/public-information material that changes over time.

The CMS should manage the publishing lifecycle of this material without hard-coding the pages into templates.

This does **not** make the CMS a legal decision system. Institutional/legal authorities remain responsible for the correctness, approval and applicability of published material.

## Required CMS page families

Create Wagtail-managed page types or a clearly structured legal section for:

### Privacy

- Privacy Policy
- Data Protection / Privacy Notice
- Cookie Policy where applicable
- Personal Data Rights / Requests information where applicable

### Website use

- Terms of Use
- Website Usage Policy
- Copyright Notice
- Disclaimer
- Accessibility Statement
- Website Security Contact

### Institutional policies

Examples:

- Information Security Policy
- Records/Document Retention Policy
- Website Content Policy
- Social Media Policy
- Accessibility Policy
- Procurement-related public information
- HR/public employment policies where appropriate
- Research-related policies
- Ethics/integrity policies
- Conflict-of-interest policy
- Open-access/publication policy
- Data management policy

Only create a specific policy category when the institution actually needs it.

### Public information

Depending on jurisdiction and institutional requirements:

- Right to Information / public-information page
- Public information officer details
- Disclosure information
- Annual reports
- Statutory notices
- Public notices
- Grievance information
- Contact points
- Tender/procurement notices

Do not invent statutory requirements.

## LegalPage model

Recommended fields:

```text
title
slug
policy_type
summary
body
version
status
effective_from
effective_until
last_reviewed_at
next_review_at
owner_department
approving_authority
approval_reference
approval_date
related_documents
contact_email
contact_phone
```

## Policy type choices

Use controlled choices such as:

```text
Privacy
Accessibility
Copyright
Disclaimer
Terms of Use
Cookie Policy
Institutional Policy
Research Policy
Information Security
Public Information
Procurement
HR
Other
```

The exact list must remain extensible.

## Status

```text
Draft
Under Review
Approved
Published
Archived
```

## Versioning

Display the version publicly where appropriate.

Example:

```text
Privacy Policy
Version 2.1
Effective from 01 October 2026
Last reviewed 15 September 2026
```

Do not expose internal workflow notes.

## Approval

For policy/legal content:

```text
Editor
  |
  v
Reviewer
  |
  v
Approving authority
  |
  v
Publisher
  |
  v
Published
```

The exact approval authority is institution-specific.

## Review reminders

Where practical, support:

- next review date
- owner
- review status

A future dashboard may show:

```text
Policies due for review
Policies overdue
Draft policies
Policies awaiting approval
```

Do not automatically change the legal validity of a policy merely because its review date has passed.

## Related documents

Allow links to:

- PDF policies
- circulars
- resolutions
- board/committee documents
- forms
- supporting guidance

Ensure private documents cannot accidentally become public.

## Footer

The public website should provide a discoverable legal area, for example:

```text
Privacy
Accessibility
Copyright
Disclaimer
Terms of Use
Policies
```

Do not hide required public information.

## Legal content seed data

Seed only placeholder text such as:

> This is a demonstration policy page. Replace this content with the institution-approved policy before publication.

Every seed legal page should be clearly marked as demo/unapproved.

Never seed fabricated:

- statutory references
- registration numbers
- government notifications
- legal claims
- officer names
- legal deadlines
- compliance certifications

## CMS editorial guidance

Editors should see:

- policy type
- version
- status
- effective date
- review date
- owner
- approval reference

This reduces accidental publication of outdated policy documents.

## Accessibility

Legal pages should be particularly readable:

- clear heading hierarchy
- table of contents for long policies
- sufficient line length
- readable typography
- document download metadata
- keyboard navigation
- print-friendly presentation where useful

## SEO

Legal pages should normally be indexable if intended for public access.

Some internal/private policy material must not be publicly indexed.

Use page-level robots controls where required.

## Disclaimer

This document describes CMS architecture, not legal advice.

The institution must determine which legal/policy pages it is required to publish and must have the content reviewed by the appropriate authority.
