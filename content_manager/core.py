from django import forms
from django.forms.utils import ErrorList
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from dsfr.constants import COLOR_CHOICES
from wagtail import blocks
from wagtail.blocks.struct_block import StructBlockAdapter, StructBlockValidationError
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageBlock
from wagtail.telepath import register

from content_manager.constants import (
    BUTTON_ICON_SIDE,
    BUTTON_TYPE_CHOICES,
    BUTTONS_ALIGN_CHOICES,
    LINK_ICON_CHOICES,
    LINK_SIZE_CHOICES,
)
from content_manager.widgets import DsfrIconPickerWidget

Image = get_image_model()


## Image
class ImageBlockWithDefault(ImageBlock):
    def __init__(
        self, *args, default_image_title=None, default_image_decorative=True, default_image_alt_text="", **kwargs
    ):
        self._default_image_title = default_image_title
        self._default_image_alt_text = default_image_alt_text
        self._default_image_decorative = default_image_decorative
        super().__init__(*args, **kwargs)

        if "decorative" in self.child_blocks:
            self.child_blocks["decorative"].field.help_text = _(
                "Check if the image is purely decorative. " "In this case, the alt attribute (alt text) will be empty."
            )
        if "alt_text" in self.child_blocks:
            self.child_blocks["alt_text"].field.help_text = _(
                "Used by screen readers if the image is not marked as decorative."
                "Describe the content or purpose of the image in a short, clear sentence."
            )

    def get_default(self):
        if self._default_image_title:
            image = Image.objects.filter(title=self._default_image_title).first()
            if image:
                return {
                    "image": image,
                    "alt_text": self._default_image_alt_text,
                    "decorative": self._default_image_decorative,
                }
        return super().get_default()


## Meta-blocks
class LinkStructValue(blocks.StructValue):
    def url(self):
        link = self.get("external_url", "")

        page = self.get("page")
        document = self.get("document")

        if page:
            link = page.url
        elif document:
            link = document.url

        return link


class LinkWithoutLabelBlock(blocks.StructBlock):
    LINK_TYPE_CHOICES = [
        ("page", _("Page")),
        ("external_url", _("External URL")),
        ("document", _("Document")),
    ]

    link_type = blocks.ChoiceBlock(
        choices=LINK_TYPE_CHOICES,
        required=False,
        label=_("Link type"),
        help_text=_("Select the type of link."),
    )
    page = blocks.PageChooserBlock(
        label=_("Page"),
        required=False,
        help_text=_("Link to a page of this site. Use either this, the document, or the external URL parameter."),
    )
    document = DocumentChooserBlock(
        label=_("Document"),
        help_text=_("Use either this, the external URL or the page parameter."),
        required=False,
    )
    external_url = blocks.URLBlock(
        label=_("External URL"),
        required=False,
        help_text=_("Use either this, the document or the page parameter."),
    )

    class Meta:
        value_class = LinkStructValue
        icon = "link"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_types = [choice[0] for choice in self.LINK_TYPE_CHOICES]

    def clean(self, value):
        errors = {}
        selected_link_type = value.get("link_type")
        if not selected_link_type:
            for link_type in self.link_types:
                if value.get(link_type):
                    selected_link_type = link_type
                    value["link_type"] = link_type
                    break
        match selected_link_type:
            case "page":
                internal_page = value.get("page")
                if not internal_page:
                    errors["page"] = ErrorList([_("Please select a page to link to")])
            case "external_url":
                external_url = value.get("external_url")
                if not external_url:
                    errors["external_url"] = ErrorList([_("Please enter a URL")])
            case "document":
                document = value.get("document")
                if not document:
                    errors["document"] = ErrorList([_("Please select a document to link to")])
        if errors:
            raise StructBlockValidationError(block_errors=errors)

        for link_type in self.link_types:
            if link_type != selected_link_type:
                value[link_type] = None
        return super().clean(value)


class LinkBlock(LinkWithoutLabelBlock):
    text = blocks.CharBlock(label=_("Link label"), required=False)

    class Meta:
        value_class = LinkStructValue
        icon = "link"


class BackgroundColorChoiceBlock(blocks.ChoiceBlock):
    choices = COLOR_CHOICES

    class Meta:
        icon = "view"


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


class LinksVerticalListBlock(blocks.StreamBlock):
    link = LinkBlock(label=_("Link"))

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/links_vertical_list.html"


class ButtonBlock(LinkWithoutLabelBlock):
    text = blocks.CharBlock(label=_("Button label"), required=False)
    button_type = blocks.ChoiceBlock(label=_("Button type"), choices=BUTTON_TYPE_CHOICES, required=False)
    icon_class = IconPickerBlock(label=_("Icon"), required=False)
    icon_side = blocks.ChoiceBlock(
        label=_("Icon side"),
        choices=BUTTON_ICON_SIDE,
        required=False,
        default="",
    )

    class Meta:
        value_class = LinkStructValue
        icon = "link"


class ButtonsHorizontalListBlock(blocks.StreamBlock):
    button = ButtonBlock(label=_("Button"))

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/buttons_horizontal_list.html"


class ButtonsVerticalListBlock(blocks.StreamBlock):
    button = ButtonBlock(label=_("Button"))

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/buttons_vertical_list.html"


class ButtonsListBlock(blocks.StructBlock):
    buttons = ButtonsHorizontalListBlock(
        label=_("Buttons"),
        help_text=_(
            """Please use only one primary button.
            If you use icons, use them on all buttons and align them on the same side."""
        ),
    )
    position = blocks.ChoiceBlock(label=_("Position"), choices=BUTTONS_ALIGN_CHOICES, default="", required=False)

    class Meta:
        icon = "list-ul"
        template = "content_manager/blocks/buttons_list.html"


class SingleLinkBlock(LinkBlock):
    icon = blocks.ChoiceBlock(
        label=_("Icon"),
        help_text=_("Only used for internal links."),
        choices=LINK_ICON_CHOICES,
        required=False,
        default="",
    )
    size = blocks.ChoiceBlock(
        label=_("Size"),
        choices=LINK_SIZE_CHOICES,
        required=False,
        default="",
    )

    class Meta:
        value_class = LinkStructValue
        icon = "link"
        template = "content_manager/blocks/link.html"


class BlockMarginStructValue(blocks.StructValue):
    def vertical_margin(self):
        margin = []

        top_margin = self.get("top_margin", None)
        if top_margin:
            margin.append(f"fr-mt-{top_margin}w")

        bottom_margin = self.get("bottom_margin", None)
        if bottom_margin:
            margin.append(f"fr-mb-{bottom_margin}w")

        return " ".join(margin)


class MarginBlock(blocks.StructBlock):
    top_margin = blocks.IntegerBlock(
        label=_("Top margin"),
        min_value=0,
        max_value=15,
        default=5,
        required=False,
    )
    bottom_margin = blocks.IntegerBlock(
        label=_("Bottom margin"),
        min_value=0,
        max_value=15,
        default=5,
        required=False,
    )

    class Meta:
        value_class = BlockMarginStructValue


class LayoutBlock(MarginBlock):
    background_color = BackgroundColorChoiceBlock(
        label=_("Background color"),
        required=False,
        help_text=_(
            "Uses the French Design System colors.<br>"
            "If you want to design a classic website, choose the colour ‘white’ or ‘French blue’."
        ),
    )

    class Meta:
        help_text = _("This part allow you to choose the layout of your block (background, margin..) ")


## Adapter
class LinkBlockAdapter(StructBlockAdapter):
    js_constructor = "blocks.links.LinkBlock"

    def js_args(self, block):
        args = super().js_args(block)
        args[2]["link_types"] = block.link_types
        return args

    @cached_property
    def media(self):
        from django import forms

        structblock_media = super().media
        return forms.Media(
            js=structblock_media._js + ["js/link-block.js"],
        )


register(LinkBlockAdapter(), LinkWithoutLabelBlock)
