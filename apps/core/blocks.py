"""
Core app — reusable StreamField blocks for institutional page composition.
"""

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock

RICHTEXT_FEATURES = [
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "ol",
    "ul",
    "hr",
    "link",
    "document-link",
    "blockquote",
]


class HeadingBlock(StructBlock):
    """Section heading with optional anchor ID."""

    text = CharBlock(required=True, max_length=200)
    level = ChoiceBlock(
        choices=[("h2", "H2"), ("h3", "H3"), ("h4", "H4")],
        default="h2",
    )
    anchor_id = CharBlock(
        required=False,
        max_length=80,
        help_text="Optional anchor for in-page links (e.g. 'contact-us').",
    )

    class Meta:
        template = "blocks/heading_block.html"
        icon = "title"
        label = "Heading"


class RichBodyBlock(RichTextBlock):
    """Standard rich text block with controlled features."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("features", RICHTEXT_FEATURES)
        super().__init__(*args, **kwargs)

    class Meta:
        template = "blocks/richtext_block.html"
        icon = "pilcrow"
        label = "Rich text"


class ImageBlock(StructBlock):
    """Image with mandatory alt text and optional caption."""

    image = ImageChooserBlock(required=True)
    alt_text = CharBlock(
        required=True,
        max_length=200,
        help_text="Descriptive alt text for screen readers. Leave blank only for decorative images.",
    )
    caption = CharBlock(required=False, max_length=300)
    full_width = BooleanBlock(required=False, default=False, label="Full-width image")

    class Meta:
        template = "blocks/image_block.html"
        icon = "image"
        label = "Image"


class QuoteBlock(StructBlock):
    """Pull quote with optional attribution."""

    text = TextBlock(required=True)
    attribution = CharBlock(required=False, max_length=200)
    attribution_title = CharBlock(required=False, max_length=200)

    class Meta:
        template = "blocks/quote_block.html"
        icon = "openquote"
        label = "Quote"


class CallToActionBlock(StructBlock):
    """Call to action — title, text and a button link."""

    title = CharBlock(required=True, max_length=200)
    text = TextBlock(required=False)
    button_label = CharBlock(required=True, max_length=100, default="Learn more")
    button_page = PageChooserBlock(required=False)
    button_url = URLBlock(
        required=False, help_text="External URL (used if no page selected)."
    )

    class Meta:
        template = "blocks/cta_block.html"
        icon = "pick"
        label = "Call to action"


class DocumentListBlock(StructBlock):
    """List of downloadable documents."""

    title = CharBlock(required=False, max_length=200)
    documents = ListBlock(
        StructBlock(
            [
                ("document", DocumentChooserBlock()),
                ("label", CharBlock(required=False, max_length=200)),
            ]
        )
    )

    class Meta:
        template = "blocks/document_list_block.html"
        icon = "doc-full"
        label = "Document list"


class NoticeBlock(StructBlock):
    """Inline notice or alert within page body."""

    notice_type = ChoiceBlock(
        choices=[
            ("info", "Information"),
            ("warning", "Warning"),
            ("important", "Important"),
            ("success", "Success"),
        ],
        default="info",
    )
    title = CharBlock(required=False, max_length=200)
    text = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        template = "blocks/notice_block.html"
        icon = "warning"
        label = "Notice"


class AccordionItemBlock(StructBlock):
    """Single accordion item."""

    question = CharBlock(required=True, max_length=300)
    answer = RichTextBlock(features=RICHTEXT_FEATURES)


class AccordionBlock(StructBlock):
    """Expandable FAQ-style accordion."""

    title = CharBlock(required=False, max_length=200)
    items = ListBlock(AccordionItemBlock())

    class Meta:
        template = "blocks/accordion_block.html"
        icon = "list-ul"
        label = "Accordion / FAQ"


class StatisticItem(StructBlock):
    """Single statistic — number + label."""

    value = CharBlock(required=True, max_length=50, help_text="e.g. '500+', '₹12 Cr'")
    label = CharBlock(required=True, max_length=100)
    description = CharBlock(required=False, max_length=200)


class StatisticsBlock(StructBlock):
    """Strip of institutional statistics."""

    title = CharBlock(required=False, max_length=200)
    items = ListBlock(StatisticItem(), min_num=2, max_num=6)

    class Meta:
        template = "blocks/statistics_block.html"
        icon = "order"
        label = "Statistics"


class EmbedBlock(EmbedBlock):
    """Embedded media (video, presentation)."""

    class Meta:
        template = "blocks/embed_block.html"
        icon = "media"
        label = "Embed"


class InternalLinkBlock(StructBlock):
    """Link to an internal page."""

    page = PageChooserBlock(required=True)
    label = CharBlock(
        required=False,
        max_length=200,
        help_text="Override the page title as link label.",
    )


class ExternalLinkBlock(StructBlock):
    """Link to an external URL."""

    url = URLBlock(required=True)
    label = CharBlock(required=True, max_length=200)
    opens_new_tab = BooleanBlock(required=False, default=True)


class LinkListBlock(StructBlock):
    """List of internal or external links."""

    title = CharBlock(required=False, max_length=200)
    links = StreamBlock(
        [
            ("internal", InternalLinkBlock()),
            ("external", ExternalLinkBlock()),
        ]
    )

    class Meta:
        template = "blocks/link_list_block.html"
        icon = "link"
        label = "Link list"


# The standard body StreamField for general content pages.
STANDARD_BODY_BLOCKS = [
    ("heading", HeadingBlock()),
    ("rich_text", RichBodyBlock()),
    ("image", ImageBlock()),
    ("quote", QuoteBlock()),
    ("call_to_action", CallToActionBlock()),
    ("document_list", DocumentListBlock()),
    ("notice", NoticeBlock()),
    ("accordion", AccordionBlock()),
    ("statistics", StatisticsBlock()),
    ("embed", EmbedBlock()),
    ("link_list", LinkListBlock()),
]
