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


class LinkBlock(blocks.StructBlock):
    text = blocks.CharBlock(label=_("Link text"), required=False)
    page = blocks.PageChooserBlock(
        label=_("Page"),
        required=False,
        help_text=_("Link to a page of this site. Use either this or the external URL parameter."),
    )
    external_url = blocks.URLBlock(
        label=_("External URL"), required=False, help_text=_("Use either this or the Page parameter.")
    )

    class Meta:
        value_class = LinkStructValue


class LinkWithoutLabelBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(
        label=_("Page"),
        required=False,
        help_text=_("Link to a page of this site. Use either this or the external URL parameter."),
    )
    external_url = blocks.URLBlock(
        label=_("External URL"), required=False, help_text=_("Use either this or the Page parameter.")
    )

    class Meta:
        value_class = LinkStructValue


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
    title = blocks.CharBlock(label="Titre du message", required=False)
    description = blocks.TextBlock(label="Texte du message", required=False)
    level = blocks.ChoiceBlock(label="Type de message", choices=LEVEL_CHOICES)
    heading_tag = blocks.ChoiceBlock(
        label="Niveau de titre",
        choices=HEADING_CHOICES,
        default="h3",
        help_text="À adapter à la structure de la page. Par défaut en-tête 3.",
    )


class CalloutBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de la mise en avant", required=False)
    text = blocks.TextBlock(label="Texte mis en avant", required=False)
    heading_tag = blocks.ChoiceBlock(
        label="Niveau de titre",
        choices=HEADING_CHOICES,
        default="h3",
        help_text="À adapter à la structure de la page. Par défaut en-tête 3.",
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
        help_text="Accessibilité : Le titre doit décrire, de façon claire et concise, le contenu embarqué.",
    )
    url = blocks.URLBlock(
        label="Lien du cadre intégré",
        help_text="Exemple pour Tally : https://tally.so/embed/w2jMRa",
    )
    height = blocks.IntegerBlock(label="Hauteur en pixels")


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
    link = LinkBlock(required=False)
    link_label = blocks.CharBlock(
        label="Titre du lien",
        help_text="Le lien apparait en bas du bloc de droite, avec une flèche",
        required=False,
    )
    page = blocks.PageChooserBlock(label="Lien interne", required=False)
    link_url = blocks.URLBlock(label="Lien externe", required=False)

    class Meta:
        icon = "image"


class ImageBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), required=False)
    image = ImageChooserBlock(label="Illustration")
    alt = blocks.CharBlock(label="Texte alternatif (description textuelle de l’image)", required=False)
    caption = blocks.CharBlock(label="Légende", required=False)
    url = blocks.URLBlock(label="Lien", required=False)

    class Meta:
        icon = "image"


class QuoteBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Illustration (à gauche)", required=False)
    quote = blocks.CharBlock(label="Citation")
    author_name = blocks.CharBlock(label="Nom de l’auteur")
    author_title = blocks.CharBlock(label="Titre de l’auteur")


class SeparatorBlock(blocks.StructBlock):
    top_margin = blocks.IntegerBlock(label="Espacement au dessus", min_value=0, max_value=15, default=3)
    bottom_margin = blocks.IntegerBlock(label="Espacement en dessous", min_value=0, max_value=15, default=3)


class StepBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de l’étape")
    detail = blocks.TextBlock(label="Détail")


class StepsListBlock(blocks.StreamBlock):
    step = StepBlock(label="Étape")


class StepperBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"))
    total = blocks.IntegerBlock(label="Nombre d’étapes")
    current = blocks.IntegerBlock(label="Étape en cours")
    steps = StepsListBlock(label="Les étapes")


class TextAndCTA(blocks.StructBlock):
    text = blocks.RichTextBlock(label=_("Rich text"), required=False)
    cta_label = blocks.CharBlock(
        label="Titre de l’appel à l’action",
        help_text="Le lien apparait comme un bouton sous le bloc de texte",
        required=False,
    )
    cta_url = blocks.CharBlock(label="Lien", required=False)


class VideoBlock(blocks.StructBlock):
    title = blocks.CharBlock(label=_("Title"), required=False)
    caption = blocks.CharBlock(label="Légende")
    url = blocks.URLBlock(
        label="Lien de la vidéo",
        help_text="URL au format « embed » (Ex. : https://www.youtube.com/embed/gLzXOViPX-0)",
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
    bg_image = ImageChooserBlock(label="Image d’arrière plan", required=False)
    bg_color_class = BackgroundColorChoiceBlock(
        label="Couleur d’arrière-plan",
        required=False,
        help_text="Utilise les couleurs du système de design de l’État",
    )
    bg_color = blocks.RegexBlock(
        label="Couleur d’arrière-plan au format hexa (Ex: #f5f5fe)",
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        help_text="(Obsolète, sera retiré dans une future mise à jour. Remplacez-le par la couleur d’arrière-plan)",
        error_messages={"invalid": "La couleur n’est pas correcte, le format doit être #fff ou #f5f5fe"},
        required=False,
    )
    title = blocks.CharBlock(label=_("Title"), required=False)
    columns = MultiColumnsBlock(label="Multi-colonnes")


STREAMFIELD_COMMON_BLOCKS = [
    ("paragraph", blocks.RichTextBlock(label=_("Rich text"))),
    ("badges_list", BadgesListBlock(label=_("Badge list"))),
    ("image", ImageBlock()),
    (
        "imageandtext",
        ImageAndTextBlock(label="Bloc image et texte"),
    ),
    ("alert", AlertBlock(label="Message d’alerte")),
    ("callout", CalloutBlock(label="Texte mise en avant")),
    ("quote", QuoteBlock(label="Citation")),
    ("video", VideoBlock(label="Vidéo")),
    ("multicolumns", MultiColumnsWithTitleBlock(label="Multi-colonnes")),
    ("accordions", AccordionsBlock(label="Accordéons")),
    ("stepper", StepperBlock(label="Étapes")),
    ("separator", SeparatorBlock(label="Séparateur")),
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
                help_text="""Avertissement : Utilisez le bloc HTML avec précaution.
                Un code malveillant peut compromettre la sécurité du site.""",
            ),
        )
    ]
