from django.utils.translation import gettext_lazy as _
from wagtail import blocks

from content_manager.blocks import ContactCardBlock, ImageAndTextBlock, MultiColumnsWithTitleBlock, QuoteBlock

COLOPHON_BLOCKS = [
    ("paragraph", blocks.RichTextBlock(label=_("Rich text"))),
    (
        "imageandtext",
        ImageAndTextBlock(label="Bloc image et texte"),
    ),
    ("quote", QuoteBlock(label="Citation")),
    ("multicolumns", MultiColumnsWithTitleBlock(label="Multi-colonnes")),
    ("contact_card", ContactCardBlock(label=_("Contact card"))),
]
