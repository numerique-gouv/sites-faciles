from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ThreeCardsBlock(blocks.StructBlock):
    # Bloc avec trois cartes, une principale à gauche et deux secondaires à droite
    main_image = ImageChooserBlock(required=True, help_text=_("Main card image"))
    main_title = blocks.TextBlock(required=True, help_text=_("Main card title"))
    main_text = blocks.RichTextBlock(required=True, help_text=_("Main card text"))
    main_page_link = blocks.PageChooserBlock(required=False, help_text=_("Link to a page"))
    main_url_link = blocks.URLBlock(required=False, help_text=_("Link to an external URL"))

    top_right_image = ImageChooserBlock(required=True, help_text=_("Top right card image"))
    top_right_text = blocks.RichTextBlock(required=True, help_text=_("Top right card text"))
    top_right_button_label = blocks.TextBlock(required=True, help_text=_("Top right card button label"))
    top_right_page_link = blocks.PageChooserBlock(required=False, help_text=_("Link to a page"))
    top_right_url_link = blocks.URLBlock(required=False, help_text=_("Link to an external URL"))

    bottom_right_image = ImageChooserBlock(required=True, help_text=_("Bottom right card image"))
    bottom_right_text = blocks.RichTextBlock(required=True, help_text=_("Bottom right card text"))
    bottom_right_button_label = blocks.TextBlock(required=True, help_text=_("Bottom right card button label"))
    bottom_right_page_link = blocks.PageChooserBlock(required=False, help_text=_("Link to a page"))
    bottom_right_url_link = blocks.URLBlock(required=False, help_text=_("Link to an external URL"))

    class Meta:
        template = "numerique_gouv/blocks/three_cards.html"
        icon = "image"
        label = "Headline cards"


STREAMFIELD_NUMERIQUE_BLOCKS = [("three_cards", ThreeCardsBlock(label=_("Headline cards")))]
