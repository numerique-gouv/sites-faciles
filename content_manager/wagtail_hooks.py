import wagtail.admin.rich_text.editors.draftail.features as draftail_features
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import InlineStyleElementHandler


@hooks.register("register_rich_text_features")
def register_text_colors(features):
    """
    Register text color features: blue and white (black is default)
    """
    colors = [
        {
            "feature_name": "blue_text",
            "type": "BLUETEXT",
            "label": "🔵",
            "description": "Texte bleu",
            "color": "#000091",
            "css_class": "cmsfr-text--blue",
        },
        {
            "feature_name": "white_text",
            "type": "WHITETEXT",
            "label": "⚪",
            "description": "Texte blanc",
            "color": "#ffffff",
            "css_class": "cmsfr-text--white",
        },
    ]

    for color_config in colors:
        control = {
            "type": color_config["type"],
            "label": color_config["label"],
            "description": color_config["description"],
            "icon": "pilcrow",
            "style": {"color": color_config["color"]},
        }

        features.register_editor_plugin(
            "draftail", color_config["feature_name"], draftail_features.InlineStyleFeature(control)
        )

        db_conversion = {
            "from_database_format": {
                f'span[class="{color_config["css_class"]}"]': InlineStyleElementHandler(color_config["type"])
            },
            "to_database_format": {"style_map": {color_config["type"]: f'span class="{color_config["css_class"]}"'}},
        }

        features.register_converter_rule("contentstate", color_config["feature_name"], db_conversion)
        features.default_features.append(color_config["feature_name"])
