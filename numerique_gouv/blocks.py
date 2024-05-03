from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ThreeCardsBlock(blocks.StructBlock):
    # Bloc avec trois cartes, une principale à gauche et deux secondaires à droite
    main_image = ImageChooserBlock(required=True, help_text=_("Image de la carte principale"))
    main_title = blocks.TextBlock(required=True, help_text=_("Titre de la carte principale"))
    main_text = blocks.RichTextBlock(required=True, help_text=_("Texte de la carte principale"))
    main_page_link = blocks.PageChooserBlock(required=False, help_text=_("Lien vers une page"))
    main_url_link = blocks.URLBlock(required=False, help_text=_("Lien vers une URL externe"))

    secondary_image = ImageChooserBlock(required=True, help_text=_("Image de la deuxième carte"))
    secondary_text = blocks.RichTextBlock(required=True, help_text=_("Texte de la deuxième carte"))
    secondary_button_label = blocks.TextBlock(required=True, help_text=_("Texte du bouton de la deuxième carte"))
    secondary_page_link = blocks.PageChooserBlock(required=False, help_text=_("Lien vers une page"))
    secondary_url_link = blocks.URLBlock(required=False, help_text=_("Lien vers une URL externe"))

    tertiary_image = ImageChooserBlock(required=True, help_text=_("Image de la troisième carte"))
    tertiary_text = blocks.RichTextBlock(required=True, help_text=_("Texte de la troisième carte"))
    tertiary_button_label = blocks.TextBlock(required=True, help_text=_("Texte du bouton de la troisième carte"))
    tertiary_page_link = blocks.PageChooserBlock(required=False, help_text=_("Lien vers une page"))
    tertiary_url_link = blocks.URLBlock(required=False, help_text=_("Lien vers une URL externe"))

    class Meta:
        template = "numerique_gouv/blocks/three_cards.html"
        icon = "image"
        label = "Unes"


STREAMFIELD_NUMERIQUE_BLOCKS = [("three_cards", ThreeCardsBlock(label=_("Unes")))]
