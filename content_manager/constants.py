from django.utils.translation import gettext_lazy as _


LIMITED_RICHTEXTFIELD_FEATURES = [
    "bold",
    "italic",
    "link",
    "document-link",
    "superscript",
    "subscript",
    "strikethrough",
]

HEADING_CHOICES = [
    ("h2", _("Heading 2")),
    ("h3", _("Heading 3")),
    ("h4", _("Heading 4")),
    ("h5", _("Heading 5")),
    ("h6", _("Heading 6")),
    ("p", _("Paragraph")),
]

LEVEL_CHOICES = [
    ("error", _("Error")),
    ("success", _("Success")),
    ("info", _("Information")),
    ("warning", _("Warning")),
]

HORIZONTAL_CARD_IMAGE_RATIOS = [
    ("fr-card--horizontal-tier", "1/3"),
    ("fr-card--horizontal-half", "50/50"),
]

MEDIA_WIDTH_CHOICES = [
    ("fr-content-media--sm", _("Small")),
    ("", _("Medium")),
    ("fr-content-media--lg", _("Large")),
]
