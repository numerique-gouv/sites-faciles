from wagtail import blocks

from content_manager.blocks import (
    AccordionsBlock,
    AlertBlock,
    CalloutBlock,
    HeroBlock,
    ImageAndTextBlock,
    ImageBlock,
    MultiColumnsWithTitleBlock,
    QuoteBlock,
    SeparatorBlock,
    StepperBlock,
    TitleBlock,
    VideoBlock,
)


STREAMFIELD_TITLE_FIELDS = [
    ("hero", HeroBlock(label="Section promotionnelle")),
    ("title", TitleBlock(label="Titre de page")),
]

STREAMFIELD_COMMON_FIELDS = [
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
]

STREAMFIELD_ALL_FIELDS = STREAMFIELD_TITLE_FIELDS + STREAMFIELD_COMMON_FIELDS
