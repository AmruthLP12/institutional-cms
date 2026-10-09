"""
Legal app — policy and legal/public-information page models.

IMPORTANT: The `approval_status` field is distinct from Wagtail's publish state.
A LegalPage must have approval_status='published' AND be live in Wagtail
to be displayed publicly. CMS publication alone is not equivalent to
institutional/legal approval. This is documented in docs/legal-pages.md.
"""

from django.db import models
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.fields import RichTextField, StreamField
from wagtail.search import index

from apps.core.blocks import STANDARD_BODY_BLOCKS
from apps.core.models import BasePage


class LegalIndexPage(BasePage):
    """
    Landing page for the legal / policy section.
    Lists all published (approval_status=published) LegalPages grouped by policy type.
    """

    intro = RichTextField(
        blank=True,
        features=["bold", "italic", "link"],
        help_text="Introduction shown at the top of the policies index.",
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = BasePage.promote_panels

    subpage_types = ["legal.LegalPage"]
    parent_page_types = ["wagtailcore.Page"]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Only pages that are live in Wagtail, visible, AND institutionally approved
        approved_pages = (
            LegalPage.objects.live()
            .public()
            .visible()
            .filter(approval_status=LegalPage.ApprovalStatus.PUBLISHED)
            .order_by("policy_type", "title")
        )

        # Group by policy_type for display
        grouped = {}
        for page in approved_pages:
            type_label = page.get_policy_type_display()
            grouped.setdefault(type_label, []).append(page)

        context["grouped_policies"] = grouped
        context["all_policies"] = approved_pages
        return context

    class Meta:
        verbose_name = "Legal & policies index"


class LegalPage(BasePage):
    """
    Legal, policy, and public-information page.

    This model captures all institutional policy metadata as required by
    docs/legal-pages.md. The approval_status is a SEPARATE concern from
    Wagtail's publish state. Editors must not confuse CMS publication
    with institutional/legal approval.

    A LegalPage is publicly visible ONLY when:
      1. It is live in Wagtail (standard Wagtail publish)
      AND
      2. approval_status == 'published'

    This is enforced by the `serve()` override below.
    """

    class PolicyType(models.TextChoices):
        PRIVACY = "privacy", "Privacy Policy"
        ACCESSIBILITY = "accessibility", "Accessibility Statement"
        COPYRIGHT = "copyright", "Copyright Notice"
        DISCLAIMER = "disclaimer", "Disclaimer"
        TERMS = "terms", "Terms of Use"
        COOKIE = "cookie", "Cookie Policy"
        INSTITUTIONAL = "institutional", "Institutional Policy"
        RESEARCH = "research", "Research Policy"
        INFORMATION_SECURITY = "information_security", "Information Security"
        PUBLIC_INFORMATION = "public_information", "Public Information"
        PROCUREMENT = "procurement", "Procurement / Tenders"
        HR = "hr", "HR / Employment"
        RTI = "rti", "RTI / Right to Information"
        GRIEVANCE = "grievance", "Grievance Mechanism"
        OTHER = "other", "Other"

    class ApprovalStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        UNDER_REVIEW = "under_review", "Under Review"
        APPROVED = "approved", "Approved"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    # Policy identity
    policy_type = models.CharField(
        max_length=50,
        choices=PolicyType.choices,
        default=PolicyType.OTHER,
        db_index=True,
    )
    version = models.CharField(
        max_length=50,
        blank=True,
        help_text="Policy version number (e.g. 1.0, 2.3).",
    )

    # Approval workflow (separate from Wagtail publish)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.DRAFT,
        db_index=True,
        help_text=(
            "Institutional approval status. This is SEPARATE from Wagtail's publish action. "
            "Set to 'Published' only after the appropriate authority has reviewed and approved "
            "the content. CMS publication without institutional approval is not sufficient."
        ),
    )
    approving_authority = models.CharField(
        max_length=300,
        blank=True,
        help_text="Name or designation of the approving authority (e.g. 'Board of Governors').",
    )
    approval_reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="Official approval reference or resolution number.",
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date on which this policy was formally approved.",
    )

    # Dates
    effective_from = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Date from which this policy is effective.",
    )
    effective_until = models.DateField(
        null=True,
        blank=True,
        help_text="Date until which this policy is effective (leave blank if indefinite).",
    )
    last_reviewed_at = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last institutional review.",
    )
    next_review_at = models.DateField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Scheduled date for next review.",
    )

    # Ownership
    owner_department = models.CharField(
        max_length=300,
        blank=True,
        help_text="Department or unit responsible for this policy.",
    )

    # Content
    summary = RichTextField(
        blank=True,
        features=["bold", "italic", "link", "ol", "ul"],
        help_text="Brief summary shown at the top and in listings.",
    )
    body = StreamField(
        STANDARD_BODY_BLOCKS,
        blank=True,
        use_json_field=True,
        help_text="Full policy content.",
    )

    # Contact
    contact_email = models.EmailField(
        blank=True,
        help_text="Email address for questions about this policy.",
    )
    contact_phone = models.CharField(max_length=30, blank=True)

    # Related documents
    related_documents = StreamField(
        [
            (
                "document",
                __import__(
                    "wagtail.documents.blocks", fromlist=["DocumentChooserBlock"]
                ).DocumentChooserBlock(),
            ),
        ],
        blank=True,
        use_json_field=True,
        help_text="Supporting documents (PDF policies, circulars, forms).",
    )

    # ---- Admin panels ----
    policy_panels = [
        FieldPanel("policy_type"),
        FieldPanel("version"),
        FieldPanel("summary"),
        FieldPanel("body"),
        FieldPanel("related_documents"),
    ]

    approval_panels = [
        MultiFieldPanel(
            [
                FieldPanel("approval_status"),
                FieldPanel("approving_authority"),
                FieldPanel("approval_reference"),
                FieldPanel("approval_date"),
            ],
            heading="Approval (required before public display)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("effective_from"),
                FieldPanel("effective_until"),
                FieldPanel("last_reviewed_at"),
                FieldPanel("next_review_at"),
                FieldPanel("owner_department"),
            ],
            heading="Dates and ownership",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_email"),
                FieldPanel("contact_phone"),
            ],
            heading="Contact",
        ),
    ]

    content_panels = BasePage.content_panels + policy_panels

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Policy Content"),
            ObjectList(approval_panels, heading="Approval & Dates"),
            ObjectList(BasePage.promote_panels, heading="SEO & Sharing"),
        ]
    )

    parent_page_types = ["legal.LegalIndexPage"]
    subpage_types = []

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
        index.FilterField("approval_status"),
        index.FilterField("policy_type"),
    ]

    def serve(self, request, *args, **kwargs):
        """
        Override serve to enforce that only institutionally approved pages
        are publicly accessible, regardless of Wagtail publish state.
        """
        if self.approval_status != self.ApprovalStatus.PUBLISHED:
            from django.http import Http404

            raise Http404(
                "This policy page is not publicly available. "
                "It may be pending review or approval."
            )
        return super().serve(request, *args, **kwargs)

    class Meta:
        verbose_name = "Policy / legal page"
        verbose_name_plural = "Policy / legal pages"

    def get_approval_status_badge_class(self) -> str:
        """Return DaisyUI badge class based on approval status."""
        mapping = {
            self.ApprovalStatus.DRAFT: "badge-neutral",
            self.ApprovalStatus.UNDER_REVIEW: "badge-warning",
            self.ApprovalStatus.APPROVED: "badge-info",
            self.ApprovalStatus.PUBLISHED: "badge-success",
            self.ApprovalStatus.ARCHIVED: "badge-ghost",
        }
        return mapping.get(self.approval_status, "badge-neutral")
