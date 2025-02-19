from django.utils.translation import gettext_lazy as _

HEADER_FIELDS = [
    "header_image",
    "header_with_title",
    "header_color_class",
    "header_large",
    "header_darken",
    "header_cta_text",
    "header_cta_buttons",
    "header_cta_label",
    "header_cta_link",
]

BUTTON_TYPE_CHOICES = (
    ("fr-btn", _("Primary")),
    ("fr-btn fr-btn--secondary", _("Secundary")),
    ("fr-btn fr-btn--tertiary", _("Tertiary")),
    ("fr-btn fr-btn--tertiary-no-outline", _("Tertiary without border")),
)

BUTTON_ICON_SIDE = (
    ("fr-btn--icon-left", _("Left")),
    ("fr-btn--icon-right", _("Right")),
)

GRID_3_4_6_CHOICES = [
    ("3", "3/12"),
    ("4", "4/12"),
    ("6", "6/12"),
]

HEADING_CHOICES = [
    ("h2", _("Heading 2")),
    ("h3", _("Heading 3")),
    ("h4", _("Heading 4")),
    ("h5", _("Heading 5")),
    ("h6", _("Heading 6")),
    ("p", _("Paragraph")),
]

HEADING_CHOICES_2_5 = [
    ("h2", _("Heading 2")),
    ("h3", _("Heading 3")),
    ("h4", _("Heading 4")),
    ("h5", _("Heading 5")),
]

HORIZONTAL_CARD_IMAGE_RATIOS = [
    ("fr-card--horizontal-tier", "1/3"),
    ("fr-card--horizontal-half", "50/50"),
]

LEVEL_CHOICES = [
    ("error", _("Error")),
    ("success", _("Success")),
    ("info", _("Information")),
    ("warning", _("Warning")),
]

LIMITED_RICHTEXTFIELD_FEATURES = [
    "bold",
    "italic",
    "link",
    "document-link",
    "superscript",
    "subscript",
    "strikethrough",
]

LIMITED_RICHTEXTFIELD_FEATURES_WITHOUT_LINKS = [
    "bold",
    "italic",
    "superscript",
    "subscript",
    "strikethrough",
]

LINK_SIZE_CHOICES = [
    ("fr-link--sm", _("Small")),
    ("", _("Medium")),
    ("fr-link--lg", _("Large")),
]

LINK_ICON_CHOICES = [
    ("", _("No icon")),
    ("fr-icon-arrow-right-line fr-link--icon-right", _("Icon on the right side")),
    ("fr-icon-arrow-right-line fr-link--icon-left", _("Icon on the left side")),
]

MEDIA_WIDTH_CHOICES = [
    ("fr-content-media--sm", _("Small")),
    ("", _("Medium")),
    ("fr-content-media--lg", _("Large")),
]

TEXT_SIZE_CHOICES = [
    ("fr-text--sm", _("Small")),
    ("", _("Medium")),
    ("fr-text--lg", _("Large")),
]
