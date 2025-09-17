import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import BlockElementHandler


@hooks.register("register_rich_text_features")
def register_text_center_feature(features):
    """Register text-center block feature for Draftail editor."""
    feature_name = "text-center"
    type_ = "text-center"

    control = {
        "type": type_,
        "description": "Texte centré",
        "element": "div",
        "icon": [
            # SVG path for center align icon with rounded corners (viewBox 0 0 1024 1024)
            "M150 200 Q150 140, 210 140 L814 140 Q874 140, 874 200 Q874 260, 814 260 L210 260 Q150 260, 150 200 Z "
            "M50 512 Q50 452, 110 452 L914 452 Q974 452, 974 512 Q974 572, 914 572 L110 572 Q50 572, 50 512 Z "
            "M150 824 Q150 764, 210 764 L814 764 Q874 764, 874 824 Q874 884, 814 884 L210 884 Q150 884, 150 824 Z"
        ],
    }

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.BlockFeature(control, css={"all": ["content_manager/css/text-center.css"]}),
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {'div[class="cmsfr-text-center"]': BlockElementHandler(type_)},
            "to_database_format": {"block_map": {type_: {"element": "div", "props": {"class": "cmsfr-text-center"}}}},
        },
    )

    features.default_features.append("text-center")


@hooks.register("insert_editor_js")
def editor_js():
    return format_html('<script src="{}"></script>', static("content_manager/js/text-center.js"))
