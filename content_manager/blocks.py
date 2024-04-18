from django import forms
from django.conf import settings
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, pgettext_lazy
from dsfr.constants import COLOR_CHOICES, COLOR_CHOICES_ILLUSTRATION, COLOR_CHOICES_SYSTEM
from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock

from content_manager.constants import HEADING_CHOICES, LEVEL_CHOICES
from content_manager.widgets import DsfrIconPickerWidget


# Wagtail Block Documentation : https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html


## Meta blocks
class BackgroundColorChoiceBlock(blocks.ChoiceBlock):
    choices = COLOR_CHOICES

    class Meta:
        icon = "view"


class LinkStructValue(blocks.StructValue):
    def url(self):
        external_url = self.get("external_url")
        page = self.get("page")
        return external_url or page.url


class LinkWithoutLabelBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(
        label=_("Page"),
        required=False,
        help_text=_("Link to a page of this site. Use either this or the external URL parameter."),
    )
    external_url = blocks.URLBlock(
        label=_("External URL"),
        required=False,
        help_text=_("Use either this or the Page parameter."),
    )

    class Meta:
        value_class = LinkStructValue
        icon = "link"


class LinkBlock(LinkWithoutLabelBlock):
    text = blocks.CharBlock(label=_("Link label"), required=False)

    class Meta:
        value_class = LinkStructValue
        icon = "link"


class IconPickerBlock(blocks.FieldBlock):
    def __init__(self, required=True, help_text=None, validators=(), **kwargs):
        self.field_options = {
            "required": required,
            "help_text": help_text,
            "max_length": 70,
            "min_length": 0,
            "validators": [],
        }
        super().__init__(**kwargs)

    @cached_property
    def field(self):
        field_kwargs = {"widget": DsfrIconPickerWidget()}
        field_kwargs.update(self.field_options)
        return forms.CharField(**field_kwargs)

    class Meta:
        icon = "radio-full"


## Badges and Tags
badge_level_choices = (
    COLOR_CHOICES_SYSTEM
    + [
        ("new", _("New")),
        ("grey", _("Grey")),
    ]
    + COLOR_CHOICES_ILLUSTRATION
)


class BadgeBlock(blocks.StructBlock):
    text = blocks.CharBlock(label=_("Badge label"), required=False)
    color = blocks.ChoiceBlock(label=_("Badge color"), choices=badge_level_choices, required=False)
    hide_icon = blocks.BooleanBlock(label=_("Hide badge icon"), required=False)

    class Meta:
        template = ("content_manager/blocks/badge.html",)


class BadgesListBlock(blocks.StreamBlock):
    badge = BadgeBlock(label=_("Badge"))

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/badges_list.html"


class TagBlock(blocks.StructBlock):
    label = blocks.CharBlock(label=_("Title"))
    is_small = blocks.BooleanBlock(label=_("Small tag"), required=False)
    color = blocks.ChoiceBlock(
        label=_("Tag color"),
        choices=COLOR_CHOICES_ILLUSTRATION,
        required=False,
        help_text=_("Only for clickable tags"),
    )
    icon_class = IconPickerBlock(label=_("Icon"), required=False)
    link = LinkWithoutLabelBlock(required=False)

    class Meta:
        template = "content_manager/blocks/tag.html"


class TagListBlock(blocks.StreamBlock):
    tag = TagBlock(label=pgettext_lazy("DSFR Tag", "Tag"))

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/tags_list.html"


## Basic blocks
class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    content = blocks.RichTextBlock(label=_("Content"))


class AccordionsBlock(blocks.StreamBlock):
    title = blocks.CharBlock(label=_("Title"))
    accordion = AccordionBlock(label=_("Accordion"), min_num=1, max_num=15)


class AlertBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Message title"), required=False)
    description = blocks.TextBlock(label=_("Message text"), required=False)
    level = blocks.ChoiceBlock(label=_("Message type"), choices=LEVEL_CHOICES)
    heading_tag = blocks.ChoiceBlock(
        label=_("Heading level"),
        choices=HEADING_CHOICES,
        default="h3",
        help_text=_("Adapt to the page layout. Defaults to heading 3."),
    )


class CalloutBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Callout title"), required=False)
    text = blocks.TextBlock(label=_("Callout text"), required=False)
    heading_tag = blocks.ChoiceBlock(
        label=_("Heading level"),
        choices=HEADING_CHOICES,
        default="h3",
        help_text=_("Adapt to the page layout. Defaults to heading 3."),
    )


class CardBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    description = blocks.TextBlock(label=_("Content"))
    image = ImageChooserBlock(label=_("Image"), required=False)
    url = blocks.URLBlock(label=_("Link"), required=False, group="target")
    document = DocumentChooserBlock(
        label=_("or Document"),
        help_text=_("Select a document to make the card link to it (if the 'Link' field is not populated.)"),
        required=False,
        group="target",
    )


class IframeBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        label=_("Title"),
        help_text=_("Accessibility: The title should describe, in a clear and concise manner, the embedded content."),
    )
    url = blocks.URLBlock(
        label=_("URL of the iframe"),
        help_text=_("Example for Tally: https://tally.so/embed/w2jMRa"),
    )
    height = blocks.IntegerBlock(label=_("Height (in pixels)"))


class ImageAndTextBlock(blocks.StructBlock):
    image = ImageChooserBlock(label=_("Image"))
    image_side = blocks.ChoiceBlock(
        label=_("Side where the image is displayed"),
        choices=[
            ("left", _("Left")),
            ("right", _("Right")),
        ],
        default="right",
    )
    image_ratio = blocks.ChoiceBlock(
        label=_("Image width"),
        choices=[
            ("3", "3/12"),
            ("5", "5/12"),
            ("6", "6/12"),
        ],
        default="3",
    )
    text = blocks.RichTextBlock(label=_("Rich text"))
    link = LinkBlock(
        label=_("Link"),
        required=False,
        help_text=_("The link is shown at the bottom of the text block, with an arrow"),
    )
    link_label = blocks.CharBlock(
        label=_("Link label (obsolete)"),
        required=False,
        help_text=_(
            "This field is obsolete and will be removed in the near future. Please replace with the Link field above."
        ),
        group="obsolete",
    )
    page = blocks.PageChooserBlock(
        label=_("Internal link (obsolete)"),
        required=False,
        help_text=_(
            "This field is obsolete and will be removed in the near future. Please replace with the Link field above."
        ),
        group="obsolete",
    )
    link_url = blocks.URLBlock(
        label=_("Link URL (obsolete)"),
        required=False,
        help_text=_(
            "This field is obsolete and will be removed in the near future. Please replace with the Link field above."
        ),
        group="obsolete",
    )

    class Meta:
        icon = "image"
        template = "content_manager/blocks/image_and_text.html"


class ImageBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), required=False)
    image = ImageChooserBlock(label=_("Image"))
    alt = blocks.CharBlock(
        label=_("Alternative text (textual description of the image)"),
        required=False,
    )
    caption = blocks.CharBlock(label=_("Caption"), required=False)
    url = blocks.URLBlock(label=_("Link"), required=False)

    class Meta:
        icon = "image"


class QuoteBlock(blocks.StructBlock):
    image = ImageChooserBlock(label=_("Image"), required=False)
    quote = blocks.CharBlock(label=_("Quote"))
    author_name = blocks.CharBlock(label=_("Author name"))
    author_title = blocks.CharBlock(label=_("Author title"))


class SeparatorBlock(blocks.StructBlock):
    top_margin = blocks.IntegerBlock(label=_("Top margin"), min_value=0, max_value=15, default=3)
    bottom_margin = blocks.IntegerBlock(label=_("Bottom margin"), min_value=0, max_value=15, default=3)


class StepBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    detail = blocks.TextBlock(label=_("Detail"))


class StepsListBlock(blocks.StreamBlock):
    step = StepBlock(label=_("Step"))


class StepperBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    total = blocks.IntegerBlock(label=_("Number of steps"))
    current = blocks.IntegerBlock(label=_("Current step"))
    steps = StepsListBlock(label=_("Steps"))


class TextAndCTA(blocks.StructBlock):
    text = blocks.RichTextBlock(label=_("Rich text"), required=False)
    cta_label = blocks.CharBlock(
        label=_("Call to action label"),
        help_text=_("The link appears as a button under the text block"),
        required=False,
    )
    cta_url = blocks.CharBlock(label=_("Link"), required=False)


class VideoBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), required=False)
    caption = blocks.CharBlock(label=_("Caption"))
    url = blocks.URLBlock(
        label=_("Video URL"),
        help_text="Use embed format (e.g. : https://www.youtube.com/embed/gLzXOViPX-0)",
    )


## Multi-column blocks
class MultiColumnsBlock(blocks.StreamBlock):
    text = blocks.RichTextBlock(label=_("Rich text"))
    image = ImageBlock(label=_("Image"))
    video = VideoBlock(label=_("Video"))
    card = CardBlock(label=_("Card"))
    quote = QuoteBlock(label=_("Quote"))
    text_cta = TextAndCTA(label=_("Text and call to action"))
    iframe = IframeBlock(label=_("Iframe"))

    class Meta:
        icon = "dots-horizontal"


class MultiColumnsWithTitleBlock(blocks.StructBlock):
    bg_image = ImageChooserBlock(label=_("Background image"), required=False)
    bg_color_class = BackgroundColorChoiceBlock(
        label=_("Background color"),
        required=False,
        help_text=_("Uses the French Design System colors"),
    )
    bg_color = blocks.RegexBlock(
        label=_("Background color, hexadecimal format (obsolete)"),
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        help_text="(Obsolète, sera retiré dans une future mise à jour. Remplacez-le par la couleur d’arrière-plan)",
        error_messages={"invalid": _("Incorrect color format, must be #fff or #f5f5f5")},
        required=False,
    )
    title = blocks.CharBlock(label=_("Title"), required=False)
    columns = MultiColumnsBlock(label=_("Multiple columns"))


STREAMFIELD_COMMON_BLOCKS = [
    ("paragraph", blocks.RichTextBlock(label=_("Rich text"))),
    ("badges_list", BadgesListBlock(label=_("Badge list"))),
    ("image", ImageBlock()),
    (
        "imageandtext",
        ImageAndTextBlock(label=_("Image and text")),
    ),
    ("alert", AlertBlock(label=_("Alert message"))),
    ("callout", CalloutBlock(label=_("Callout"))),
    ("quote", QuoteBlock(label=_("Quote"))),
    ("video", VideoBlock(label=_("Video"))),
    ("multicolumns", MultiColumnsWithTitleBlock(label=_("Multiple columns"))),
    ("accordions", AccordionsBlock(label=_("Accordions"))),
    ("stepper", StepperBlock(label=_("Stepper"))),
    ("separator", SeparatorBlock(label=_("Separator"))),
    ("tags_list", TagListBlock(label=_("Tag list"))),
    ("markdown", MarkdownBlock()),
]


# See warning on https://docs.wagtail.org/en/latest/reference/streamfield/blocks.html#wagtail.blocks.RawHTMLBlock
# There is currently no way to restrict a type of block depending on user permissions,
# pending issue https://github.com/wagtail/wagtail/issues/6323
if settings.SF_ALLOW_RAW_HTML_BLOCKS is True:
    STREAMFIELD_COMMON_BLOCKS += [
        (
            "html",
            blocks.RawHTMLBlock(
                readonly=True,
                help_text=_(
                    "Warning: Use HTML block with caution. Malicious code can compromise the security of the site."
                ),
            ),
        )
    ]
