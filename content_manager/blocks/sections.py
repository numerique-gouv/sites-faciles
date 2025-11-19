from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.images import get_image_model
from wagtail.images.blocks import ImageBlock
from wagtail.telepath import register

from content_manager.constants import (
    ALIGN_HORIZONTAL_CHOICES,
    ALIGN_HORIZONTAL_CHOICES_EXTENDED,
    GRID_6_8_12_CHOICES,
    GRID_HORIZONTAL_ALIGN_CHOICES,
    IMAGE_GRID_SIZE,
    LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
)

from .basics import AccordionsBlock
from .buttons_links import ButtonBlock, LinkBlock
from .cards import VerticalCardBlock
from .layout import LayoutBlock
from .medias import ImageBlockWithDefault

Image = get_image_model()


class BaseSection(blocks.StructBlock):
    section_title = blocks.CharBlock(default=_("Section title"))
    layout = LayoutBlock(label=_("Layout"), collapsed=True)


class ResizedStructValue(StructValue):
    def extra_classes(self):
        """
        Define the extra classes for the resized text
        """
        width = self.get("width")
        alignment = self.get("alignment") or ""

        base_classes = {
            "": "cmsfr-text-content--center",
            "right": "cmsfr-text-content--right",
        }

        offsets = {
            "": {"8": "fr-col-offset-2", "6": "fr-col-offset-3"},
            "right": {"8": "fr-col-offset-4", "6": "fr-col-offset-6"},
        }

        base_class = base_classes.get(alignment, "")
        offset_class = offsets.get(alignment, {}).get(width, "")

        return f"{base_class} {offset_class}"


class ResizedTextSection(blocks.StructBlock):
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
    width = blocks.ChoiceBlock(choices=GRID_6_8_12_CHOICES, label=_("Block width"), default="8")
    alignment = blocks.ChoiceBlock(
        choices=ALIGN_HORIZONTAL_CHOICES_EXTENDED, label=_("Block alignment"), default="", required=False
    )

    class Meta:
        template = "content_manager/blocks/sections/layout_text_block.html"
        value_class = ResizedStructValue
        form_classname = "struct-block resized-text-section"


class ResizedSectionAdapter(StructBlockAdapter):
    """
    Adapter to add the styling to the admin form
    """

    @cached_property
    def media(self):
        return forms.Media(
            css={"all": ("css/admin-block/resized-block-admin.css",)},
        )


register(ResizedSectionAdapter(), ResizedTextSection)


class ImageTextCTASection(blocks.StructBlock):
    text = blocks.RichTextBlock(
        label=_("Text block"),
        features=LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
        default="<h3>Titre de la section</h3> </br> Lorem ipsum dolor sit amet, consectetur adipiscing elit, ",
    )
    position = blocks.ChoiceBlock(
        choices=ALIGN_HORIZONTAL_CHOICES,
        label=_("Text content position"),
        default="left",
        help_text=_("This field allows you to define the placement of text relative to adjacent content."),
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
    layout = LayoutBlock(label=_("Layout"), collapsed=True)

    class Meta:
        template = "content_manager/blocks/sections/image_text_cta.html"


# class ImageTextCTAMultipleSection(blocks.StructBlock):
#     items = blocks.ListBlock(ImageTextCTASection)

#     class Meta:
#         template = "content_manager/blocks/sections/image_text_cta_multiple.html"


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
        label=_("Image size of items"),
    )
    items = blocks.ListBlock(ImageAndTextItems(), collapsed=True)

    class Meta:
        template = "content_manager/blocks/sections/image_text_grid.html"
        form_classname = "struct-block image-text-grid-block"


class ImageAndTextGridAdapter(StructBlockAdapter):
    """
    Adapter to add the styling to the admin form
    """

    @cached_property
    def media(self):
        return forms.Media(
            css={"all": ("css/admin-block/image-text-grid-block-admin.css",)},
        )


register(ImageAndTextGridAdapter(), ImageAndTextGridSection)


class CTASection(BaseSection):
    text = blocks.RichTextBlock(label=_("Text"))
    button = ButtonBlock(label=_("Button"))

    class Meta:
        template = "content_manager/blocks/sections/text-cta.html"


class SpotLightItem(blocks.StreamBlock):
    card = VerticalCardBlock()


class SpotlightSection(BaseSection):
    items_per_row = blocks.ChoiceBlock(choices=[("6", "2"), ("4", "3"), ("3", "4")], default="3")
    link = LinkBlock(
        label=_("Lien de la section"),
        help_text="Ce lien apparait en haut à droite de la section s'il est complété",
        required=False,
        collapsed=True,
    )
    items = SpotLightItem()

    class Meta:
        template = "content_manager/blocks/sections/spotlight.html"


# This doesn't heritate from BaseSection to reuse AccordionsBlock component.
class AccordionSection(blocks.StructBlock):
    accordion = AccordionsBlock()
    layout = LayoutBlock(label=_("Layout"), collapsed=True)

    class Meta:
        template = "content_manager/blocks/sections/accordion_section.html"
