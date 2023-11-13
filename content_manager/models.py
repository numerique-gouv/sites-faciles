from django.db import models
from django.forms.widgets import Textarea
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index


# Wagtail Block Documentation : https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html
class HeroBlock(blocks.StructBlock):
    bg_image = ImageChooserBlock(label="Image d'arrière plan")
    bg_color = blocks.RegexBlock(
        label="Couleur d'arrière plan au format hexa (Ex: #f5f5fe)",
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        error_messages={"invalid": "La couleur n'est pas correcte, le format doit être #fff ou #f5f5fe"},
        required=False,
    )
    title = blocks.CharBlock(label="Titre")
    text = blocks.CharBlock(label="Texte", required=False)
    cta_label = blocks.CharBlock(label="Texte du bouton", required=False)
    cta_link = blocks.URLBlock(label="Lien du bouton", required=False)


class TitleBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    large = blocks.BooleanBlock(label="Large", required=False)


class ImageBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre", required=False)
    image = ImageChooserBlock(label="Illustration")
    alt = blocks.CharBlock(label="Texte alternatif (description textuelle de l'image)", required=False)
    caption = blocks.CharBlock(label="Légende", required=False)
    url = blocks.URLBlock(label="Lien", required=False)


class ImageAndTextBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Illustration (à gauche)")
    image_ratio = blocks.ChoiceBlock(
        label="Largeur de l'image",
        choices=[
            ("3", "3/12"),
            ("5", "5/12"),
            ("6", "6/12"),
        ],
    )
    text = blocks.RichTextBlock(label="Texte avec mise en forme (à droite)")
    link_label = blocks.CharBlock(
        label="Titre du lien",
        help_text="Le lien apparait en bas du bloc de droite, avec une flèche",
        required=False,
    )
    link_url = blocks.URLBlock(label="Lien", required=False)


level_choices = [
    ("error", "Erreur"),
    ("success", "Succès"),
    ("info", "Information"),
    ("warning", "Attention"),
]


class AlertBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre du message", required=False)
    description = blocks.TextBlock(label="Texte du message", required=False)
    level = blocks.ChoiceBlock(label="Type de message", choices=level_choices)


color_choices = [
    ("", "Bleu/Gris"),
    ("fr-callout--brown-caramel", "Marron"),
    ("fr-callout--green-emeraude", "Vert"),
]


class CalloutBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de la mise en vant", required=False)
    text = blocks.TextBlock(label="Texte mis en avant", required=False)


class QuoteBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Illustration (à gauche)", required=False)
    quote = blocks.CharBlock(label="Citation")
    author_name = blocks.CharBlock(label="Nom de l'auteur")
    author_title = blocks.CharBlock(label="Titre de l'auteur")


class VideoBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre", required=False)
    caption = blocks.CharBlock(label="Légende")
    url = blocks.URLBlock(
        label="Lien de la vidéo",
        help_text="URL au format 'embed' (Ex. : https://www.youtube.com/embed/gLzXOViPX-0)",
    )


badge_level_choices = [
    ("error", "Erreur"),
    ("success", "Succès"),
    ("info", "Information"),
    ("warning", "Attention"),
    ("new", "Nouveau"),
    ("grey", "Gris"),
    ("green-emeraude", "Vert"),
    ("blue-ecume", "Bleu"),
]


class CardBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    description = blocks.TextBlock(label="Texte")
    image = ImageChooserBlock(label="Image")
    url = blocks.URLBlock(label="Lien", required=False)
    document = DocumentChooserBlock(
        label="ou Document",
        help_text=(
            "Sélectionnez un document pour rendre la carte cliquable vers "
            "celui ci (si le champ `Lien` n'est pas renseigné)."
        ),
        required=False,
    )


class BadgeBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Texte du badge", required=False)
    color = blocks.ChoiceBlock(label="Couleur de badge", choices=badge_level_choices, required=False)
    hide_icon = blocks.BooleanBlock(label="Masquer l'icon du badge", required=False)


class BadgesListBlock(blocks.StreamBlock):
    badge = BadgeBlock(label="Badge")


class TextAndCTA(blocks.StructBlock):
    text = blocks.RichTextBlock(label="Texte avec mise en forme", required=False)
    cta_label = blocks.CharBlock(
        label="Titre de l'appel à l'action",
        help_text="Le lien apparait comme un bouton sous le bloc de texte",
        required=False,
    )
    cta_url = blocks.CharBlock(label="Lien", required=False)


class IframeBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        label="Titre",
        help_text="Accessibilité : Le titre doit décrire, de façon claire et concise, le contenu embarqué.",
    )
    url = blocks.URLBlock(
        label="Lien du cadre intégré",
        help_text="Exemple pour Tally : https://tally.so/embed/w2jMRa",
    )
    height = blocks.IntegerBlock(label="Hauteur en pixels")


class MultiColumnsBlock(blocks.StreamBlock):
    text = blocks.RichTextBlock(label="Texte avec mise en forme")
    image = ImageBlock(label="Image")
    video = VideoBlock(label="Vidéo")
    card = CardBlock(label="Carte")
    quote = QuoteBlock(label="Citation")
    text_cta = TextAndCTA(label="Texte et appel à l'action")
    iframe = IframeBlock(label="Cadre intégré")


class MultiColumnsWithTitleBlock(blocks.StructBlock):
    bg_image = ImageChooserBlock(label="Image d'arrière plan", required=False)
    bg_color = blocks.RegexBlock(
        label="Couleur d'arrière plan au format hexa (Ex: #f5f5fe)",
        regex=r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$",
        error_messages={"invalid": "La couleur n'est pas correcte, le format doit être #fff ou #f5f5fe"},
        required=False,
    )
    title = blocks.CharBlock(label="Titre", required=False)
    columns = MultiColumnsBlock(label="Multi-colonnes")


class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    content = blocks.RichTextBlock(label="Contenu")


class AccordionsBlock(blocks.StreamBlock):
    title = blocks.CharBlock(label="Titre")
    accordion = AccordionBlock(label="Accordéon", min_num=1, max_num=15)


class StepBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de l'étape")
    detail = blocks.TextBlock(label="Détail")


class StepsListBlock(blocks.StreamBlock):
    step = StepBlock(label="Étape")


class StepperBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    total = blocks.IntegerBlock(label="Nombre d'étape")
    current = blocks.IntegerBlock(label="Étape en cours")
    steps = StepsListBlock(label="Les étapes")


class SeparatorBlock(blocks.StructBlock):
    top_margin = blocks.IntegerBlock(label="Espacement au dessus", min_value=0, max_value=15, default=3)
    bottom_margin = blocks.IntegerBlock(label="Espacement en dessous", min_value=0, max_value=15, default=3)


class ContentPage(Page):
    body = StreamField(
        [
            ("hero", HeroBlock(label="Section promotionnelle")),
            ("title", TitleBlock(label="Titre de page")),
            ("paragraph", blocks.RichTextBlock(label="Texte avec mise en forme")),
            (
                "paragraphlarge",
                blocks.RichTextBlock(label="Texte avec mise en forme (large)"),
            ),
            ("image", ImageBlock()),
            (
                "imageandtext",
                ImageAndTextBlock(label="Bloc image à gauche et texte à droite"),
            ),
            ("alert", AlertBlock(label="Message d'alerte")),
            ("callout", CalloutBlock(label="Texte mise en avant")),
            ("quote", QuoteBlock(label="Citation")),
            ("video", VideoBlock(label="Vidéo")),
            ("multicolumns", MultiColumnsWithTitleBlock(label="Multi-colonnes")),
            ("accordions", AccordionsBlock(label="Accordéons")),
            ("stepper", StepperBlock(label="Étapes")),
            ("separator", SeparatorBlock(label="Séparateur")),
        ],
        blank=True,
        use_json_field=True,
    )

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    # Inherit search_fields from Page and add body to index
    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]


class MonospaceField(models.TextField):
    """
    A TextField which renders as a large HTML textarea with monospace font.
    """

    def formfield(self, **kwargs):
        kwargs["widget"] = Textarea(
            attrs={
                "rows": 12,
                "class": "monospace",
                "spellcheck": "false",
            }
        )
        return super().formfield(**kwargs)


@register_setting(icon="code")
class AnalyticsSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Scripts de suivi"

    head_scripts = MonospaceField(
        blank=True,
        null=True,
        verbose_name="Scripts de suivi <head>",
        help_text="Ajoutez des scripts de suivi entre les balises <head>.",
    )

    body_scripts = MonospaceField(
        blank=True,
        null=True,
        verbose_name="Scripts de suivi <body>",
        help_text="Ajoutez des scripts de suivi vers la fermeture de la balise <body>.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("head_scripts"),
                FieldPanel("body_scripts"),
            ],
            heading="Scripts de suivi",
        ),
    ]


@register_setting(icon="code")
class CmsDsfrConfig(BaseSiteSetting):
    class Meta:
        verbose_name = "Configuration du site"

    header_brand = models.CharField(
        "Institution (en-tête)",
        max_length=200,
        default="Intitulé officiel",
        help_text="""Intitulé du bloc-marques tel que défini sur la page
        https://www.gouvernement.fr/charte/charte-graphique-les-fondamentaux/le-bloc-marque""",
        blank=True,
    )
    header_brand_html = models.CharField(
        "Institution avec césure (en-tête)",
        max_length=200,
        default="Intitulé<br />officiel",
        blank=True,
        help_text="""Intitulé du bloc-marques avec des balises <br />
        pour affichage sur plusieurs lignes""",
    )
    footer_brand = models.CharField(
        "Institution (pied)",
        max_length=200,
        default="Intitulé officiel",
        blank=True,
    )

    footer_brand_html = models.CharField(
        "Institution avec césure (pied)",
        max_length=200,
        default="Intitulé<br />officiel",
        blank=True,
    )

    site_title = models.CharField(
        "Titre du site",
        max_length=200,
        default="Titre du site",
        blank=True,
    )
    site_tagline = models.CharField(
        "Sous-titre du site",
        max_length=200,
        default="Sous-titre du site",
        blank=True,
    )
    footer_description = models.TextField(
        "Description",
        default="",
        blank=True,
        help_text="Balises HTML autorisés",
    )
    mourning = models.BooleanField("Mise en berne", default=False)

    panels = [
        FieldPanel("header_brand"),
        FieldPanel("header_brand_html"),
        FieldPanel("footer_brand"),
        FieldPanel("footer_brand_html"),
        FieldPanel("site_title"),
        FieldPanel("site_tagline"),
        FieldPanel("footer_description"),
        FieldPanel("mourning"),
    ]
