from django import forms
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.blocks.struct_block import StructBlockAdapter
from wagtail.images import get_image_model
from wagtail.telepath import register

from content_manager.constants import (
    ALIGN_HORIZONTAL_CHOICES,
    ALIGN_HORIZONTAL_CHOICES_EXTENDED,
    GRID_6_8_12_CHOICES,
    GRID_HORIZONTAL_ALIGN_CHOICES,
    IMAGE_GRID_SIZE,
    LIMITED_RICHTEXTFIELD_FEATURES_WITH_HEADINGS,
    TEMPLATE_EXAMPLE_TAG_BADGE_LIST,
)

from .basics import AccordionsBlock
from .buttons_links import ButtonBlock, LinkBlock
from .cards import VerticalCardBlock
from .layout import LayoutBlock
from .medias import ImageBlockWithDefault

Image = get_image_model()


class BaseSection(blocks.StructBlock):
    section_title = blocks.CharBlock(label=_("Section title"), default="Titre de la section")
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
        label=_("Image"),
        default_image_title="Illustration Sites Faciles Femme Ordinateur",
        default_image_decorative=True,
    )
    layout = LayoutBlock(label=_("Layout"), collapsed=True)

    class Meta:
        template = "content_manager/blocks/sections/image_text_cta.html"


class ImageAndTextItems(blocks.StructBlock):
    image = ImageBlockWithDefault(label=_("Image"))
    title = blocks.CharBlock(label=_("Title"), required=True)
    text = blocks.RichTextBlock(
        default="Add a short description to help your visitors better understand what you offer.", label=_("Text")
    )


def get_listblock_default_items():
    image_A = Image.objects.get(title="Pictogrammes DSFR — System — Success")
    image_B = Image.objects.get(title="Pictogrammes DSFR — Institutions — Money")
    image_C = Image.objects.get(title="Pictogrammes DSFR — System — Warning")

    description = "Ajoutez une courte description afin d’aider vos visiteurs à mieux comprendre ce que vous proposez."
    list_block = [
        {
            "image": {"image": image_A if image_A else None, "decorative": True, "alt_text": ""},
            "title": "1er point",
            "text": description,
        },
        {
            "image": {"image": image_B if image_B else None, "decorative": True, "alt_text": ""},
            "title": "2ème point",
            "text": description,
        },
        {
            "image": {"image": image_C if image_C else None, "decorative": True, "alt_text": ""},
            "title": "3ème point",
            "text": description,
        },
    ]
    return list_block


class ImageAndTextListBlock(blocks.ListBlock):

    def get_default(self):
        titles = [
            "Pictogrammes DSFR — System — Success",
            "Pictogrammes DSFR — Institutions — Money",
            "Pictogrammes DSFR — System — Warning",
        ]

        description = (
            "Ajoutez une courte description afin d’aider vos visiteurs à mieux comprendre ce que vous proposez."
        )

        items = []
        for i, title in enumerate(titles, start=1):
            image = Image.objects.filter(title=title).first()
            items.append(
                {
                    "image": {
                        "image": image,
                        "decorative": True,
                        "alt_text": "",
                    },
                    "title": f"{i}er point" if i == 1 else f"{i}ème point",
                    "text": description,
                }
            )

        return items


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

    items_alignement = blocks.ChoiceBlock(GRID_HORIZONTAL_ALIGN_CHOICES, default="left", label=_("Items alignement"))
    # The choiceblock determines the number of columns in the grid based on the number of items desired per row.
    items_per_row = blocks.ChoiceBlock(
        choices=[("6", "2"), ("4", "3"), ("3", "4")], default="4", label=_("Items per row")
    )
    images_size = blocks.ChoiceBlock(
        IMAGE_GRID_SIZE,
        default="80",
        help_text=_(
            "Images are always displayed in a square (1:1) ratio. "
            "The maximum size is 200px; smaller images (e.g., 80px) are supported "
            "but will not be upscaled."
        ),
        label=_("Image size of items"),
    )
    items = ImageAndTextListBlock(
        ImageAndTextItems(),
        collapsed=True,
        label=_("Items"),
    )

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
    text = blocks.RichTextBlock(
        label=_("Text"),
        default="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididun",
    )
    button = ButtonBlock(
        label=_("Button"),
        default={
            "link_type": "external_url",
            "text": "Appel à l'action",
            "external_url": "https://tube.numerique.gouv.fr/",
            "button_type": "fr-btn",
            "icon_side": "--",
        },
    )

    class Meta:
        template = "content_manager/blocks/sections/text-cta.html"
        form_classname = "struct-block cta-section"


class CTAGridAdapter(StructBlockAdapter):
    """
    Adapter to add the styling to the admin form
    """

    @cached_property
    def media(self):
        return forms.Media(
            css={"all": ("css/admin-block/cta-section-grid-block-admin.css",)},
        )


register(CTAGridAdapter(), CTASection)


class SpotLightItem(blocks.StreamBlock):
    card = VerticalCardBlock()

    def get_default(self):
        image_placeholder = Image.objects.filter(title="Placeholder Sites Faciles").first()

        default_card_data = {
            "title": "Titre de l'article",
            "heading_tag": "h3",
            "description": (
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco "
            ),
            "image": {
                "image": image_placeholder,
                "decorative": True,
                "alt_text": "",
            },
            "image_ratio": "h3",
            "image_badge": [],
            "link": {
                "link_type": "--",
                "page": None,
                "external_url": "",
                "document": None,
                "anchor": "",
            },
            "top_detail_text": "",
            "top_detail_icon": {},
            "top_detail_badges_tags": TEMPLATE_EXAMPLE_TAG_BADGE_LIST,
            "bottom_detail_text": "",
            "bottom_detail_icon": {},
            "call_to_action": [],
            "grey_background": False,
            "no_background": False,
            "no_border": False,
            "shadow": False,
        }

        # StreamBlock values must be a list of (block_name, block_value)
        return [
            ("card", default_card_data),
            ("card", default_card_data),
            ("card", default_card_data),
        ]


class SpotlightSection(BaseSection):
    items_per_row = blocks.ChoiceBlock(
        choices=[("6", "2"), ("4", "3"), ("3", "4")], default="4", label=_("Items per row")
    )
    link = LinkBlock(
        label=_("Section link"),
        help_text="This link appears at the bottom left of the section if completed",
        required=False,
        collapsed=True,
    )
    items = SpotLightItem(label=_("Items"))

    class Meta:
        template = "content_manager/blocks/sections/spotlight.html"
        form_classname = "struct-block spotlight-grid-block"


class SpotlightSectionGridAdapter(StructBlockAdapter):
    """
    Adapter to add the styling to the admin form
    """

    @cached_property
    def media(self):
        return forms.Media(
            css={"all": ("css/admin-block/spotlight-grid-block-admin.css",)},
        )


register(SpotlightSectionGridAdapter(), SpotlightSection)


def get_accordion_default():
    return [
        ("title", "Titre de section"),
        ("accordion", {"title": "Titre de l'accordéon 1", "content": "<p>Contenu de l'accordéon 1</p>"}),
        ("accordion", {"title": "Titre de l'accordéon 2", "content": "<p>Contenu de l'accordéon 2</p>"}),
    ]


# This doesn't heritate from BaseSection to reuse AccordionsBlock component.
class AccordionSection(blocks.StructBlock):
    accordion = AccordionsBlock(default=get_accordion_default(), label=_("Accordion"))
    layout = LayoutBlock(
        label=_("Layout"),
        collapsed=True,
    )

    class Meta:
        template = "content_manager/blocks/sections/accordion_section.html"
