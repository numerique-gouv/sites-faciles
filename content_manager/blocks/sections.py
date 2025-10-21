from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageBlock

from content_manager.constants import (
    ALIGN_HORIZONTAL_CHOICES,
    GRID_6_8_12_CHOICES,
    GRID_HORIZONTAL_ALIGN_CHOICES,
    IMAGE_GRID_SIZE,
    LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
)

from .buttons_links import ButtonBlock
from .layout import LayoutBlock
from .medias import ImageBlockWithDefault

Image = get_image_model()


class BaseSection(blocks.StructBlock):
    layout = LayoutBlock()
    section_title = blocks.CharBlock()


class ResizedTextSection(blocks.StructBlock):
    width = blocks.ChoiceBlock(choices=GRID_6_8_12_CHOICES, label=_("Block width"))
    text = blocks.RichTextBlock(
        features=LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
        label=_("Rich text"),
        default="<h3>En savoir plus</h3> </br> Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur."
        "Excepteur sint occaecat cupidatat non proident, "
        "sunt in culpa qui officia deserunt mollit anim id est laborum.",
    )

    class Meta:
        template = "content_manager/blocks/sections/layout_text_block.html"


class ImageTextCTASection(blocks.StructBlock):
    position = blocks.ChoiceBlock(
        choices=ALIGN_HORIZONTAL_CHOICES,
        label=_("Text content position"),
        default="left",
        help_text=_("This field allows you to define the placement of text relative to adjacent content."),
    )
    text = blocks.RichTextBlock(
        label=_("Text block"),
        features=LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
        default="<h3>Titre de la section</h3> </br> Lorem ipsum dolor sit amet, consectetur adipiscing elit, ",
    )
    button = ButtonBlock(
        label=_("Button"),
        default={
            "link_type": "external_url",
            "text": "Appel à l'action",
            "external_url": "https://tube.numerique.gouv.fr/",
            "button_type": "fr-btn fr-btn--secondary",
            "icon_side": "--",
        },
    )
    image = ImageBlockWithDefault(
        label=_("Hero image"),
        default_image_title="Illustration Sites Faciles Femme Ordinateur",
        default_image_decorative=True,
    )
    layout = LayoutBlock(label=_("Layout"))

    class Meta:
        template = "content_manager/blocks/sections/image_text_cta.html"


class ImageTextCTAMultipleSection(blocks.StructBlock):
    items = blocks.ListBlock(ImageTextCTASection)

    class Meta:
        template = "content_manager/blocks/sections/image_text_cta_multiple.html"


class ImageAndTextItems(blocks.StructBlock):
    image = ImageBlock(label=_("Image"))
    title = blocks.CharBlock(label=_("title"), required=True)
    text = blocks.RichTextBlock(
        default="Add a short description to help your visitors better understand what you offer.", label=_("Text")
    )


class ImageAndTextGridSection(BaseSection):
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        size = value["images_size"]
        filter_spec = f"fill-{size}x{size}"

        rendered_items = []
        for item in value["items"]:
            rendition = item["image"].get_rendition(filter_spec) if item["image"] else None
            rendered_items.append(
                {
                    "title": item["title"],
                    "text": item["text"],
                    "rendition": rendition,
                }
            )
        context["rendered_items"] = rendered_items
        return context

    items_alignements = blocks.ChoiceBlock(GRID_HORIZONTAL_ALIGN_CHOICES, default="left")
    # The choiceblock determines the number of columns in the grid based on the number of items desired per row.
    items_per_row = blocks.ChoiceBlock(choices=[("6", "2"), ("4", "3"), ("3", "4")], default="3")
    images_size = blocks.ChoiceBlock(
        IMAGE_GRID_SIZE,
        default="80",
        help_text=_("The images displayed will always have a square ratio (1:1)."),
    )
    items = blocks.ListBlock(ImageAndTextItems())

    class Meta:
        template = "content_manager/blocks/sections/image_text_grid.html"
