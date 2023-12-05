from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


# Wagtail Block Documentation : https://docs.wagtail.org/en/stable/reference/streamfield/blocks.html

HEADING_CHOICES = [
    ("h2", "En-tête 2"),
    ("h3", "En-tête 3"),
    ("h4", "En-tête 4"),
    ("h5", "En-tête 5"),
    ("h6", "En-tête 6"),
    ("p", "Paragraphe"),
]

LEVEL_CHOICES = [
    ("error", "Erreur"),
    ("success", "Succès"),
    ("info", "Information"),
    ("warning", "Attention"),
]


## Basic blocks
class AccordionBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    content = blocks.RichTextBlock(label="Contenu")


class AccordionsBlock(blocks.StreamBlock):
    title = blocks.CharBlock(label="Titre")
    accordion = AccordionBlock(label="Accordéon", min_num=1, max_num=15)


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


class BadgeBlock(blocks.StructBlock):
    text = blocks.CharBlock(label="Texte du badge", required=False)
    color = blocks.ChoiceBlock(label="Couleur de badge", choices=badge_level_choices, required=False)
    hide_icon = blocks.BooleanBlock(label="Masquer l'icon du badge", required=False)


class BadgesListBlock(blocks.StreamBlock):
    badge = BadgeBlock(label="Badge")


class CalloutBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre de la mise en vant", required=False)
    text = blocks.TextBlock(label="Texte mis en avant", required=False)
    heading_tag = blocks.ChoiceBlock(
        label="Niveau de titre",
        choices=HEADING_CHOICES,
        default="h3",
        help_text="À adapter à la structure de la page. Par défaut en-tête 3.",
    )


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


class ImageBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre", required=False)
    image = ImageChooserBlock(label="Illustration")
    alt = blocks.CharBlock(label="Texte alternatif (description textuelle de l'image)", required=False)
    caption = blocks.CharBlock(label="Légende", required=False)
    url = blocks.URLBlock(label="Lien", required=False)


class QuoteBlock(blocks.StructBlock):
    image = ImageChooserBlock(label="Illustration (à gauche)", required=False)
    quote = blocks.CharBlock(label="Citation")
    author_name = blocks.CharBlock(label="Nom de l'auteur")
    author_title = blocks.CharBlock(label="Titre de l'auteur")


class SeparatorBlock(blocks.StructBlock):
    top_margin = blocks.IntegerBlock(label="Espacement au dessus", min_value=0, max_value=15, default=3)
    bottom_margin = blocks.IntegerBlock(label="Espacement en dessous", min_value=0, max_value=15, default=3)


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


class TextAndCTA(blocks.StructBlock):
    text = blocks.RichTextBlock(label="Texte avec mise en forme", required=False)
    cta_label = blocks.CharBlock(
        label="Titre de l'appel à l'action",
        help_text="Le lien apparait comme un bouton sous le bloc de texte",
        required=False,
    )
    cta_url = blocks.CharBlock(label="Lien", required=False)


class TitleBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre")
    large = blocks.BooleanBlock(label="Large", required=False)


class VideoBlock(blocks.StructBlock):
    title = blocks.CharBlock(label="Titre", required=False)
    caption = blocks.CharBlock(label="Légende")
    url = blocks.URLBlock(
        label="Lien de la vidéo",
        help_text="URL au format 'embed' (Ex. : https://www.youtube.com/embed/gLzXOViPX-0)",
    )


## Multi-column blocks
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
