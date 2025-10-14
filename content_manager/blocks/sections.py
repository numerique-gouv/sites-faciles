from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageBlock

from content_manager.constants import (
    GRID_6_8_12_CHOICES,
    GRID_HORIZONTAL_ALIGN_CHOICES,
    IMAGE_GRID_SIZE,
    LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
)

from .layout import LayoutBlock

Image = get_image_model()


class LayoutTextBlock(blocks.StructBlock):
    size = blocks.ChoiceBlock(choices=GRID_6_8_12_CHOICES, label=_("Block size"))
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


class ImageAndTextItems(blocks.StructBlock):
    image = ImageBlock(label=_("Image"))
    title = blocks.CharBlock(label=_("title"), required=True)
    text = blocks.RichTextBlock(
        default="Add a short description to help your visitors better understand what you offer.", label=_("Text")
    )


class BaseSection(blocks.StructBlock):
    layout = LayoutBlock()
    section_title = blocks.CharBlock()


class ImageAndTextGrid(BaseSection):
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
