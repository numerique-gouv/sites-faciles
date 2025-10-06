from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, StreamBlock, StructBlock

from content_manager.blocks import IconPickerBlock, LinkStructValue, LinkWithoutLabelBlock


class BaseMenuLinkBlock(LinkWithoutLabelBlock):
    text = CharBlock(
        label=_("Link label"),
        required=False,
        help_text=_("If this field is empty, the title of the linked page or document will be used."),
    )

    class Meta:
        value_class = LinkStructValue
        icon = "link"
        template = "menus/blocks/link.html"


class MenuLinkWithIconBlock(BaseMenuLinkBlock):
    icon_class = IconPickerBlock(label=_("Icon"), required=False)


class FooterBottomLinkBlock(BaseMenuLinkBlock):
    class Meta:
        template = "menus/blocks/footer_bottom_link.html"


class MainMenuLinkBlock(BaseMenuLinkBlock):
    class Meta:
        template = "menus/blocks/main_menu_link.html"


class MainMenuSubmenuLinkBlock(BaseMenuLinkBlock):
    class Meta:
        template = "menus/blocks/main_menu_link.html"


class MainMenuSubmenuBlock(StructBlock):
    text = CharBlock(
        label=_("Link label"),
        required=True,
        help_text=_("If this field is empty, the title of the linked page or document will be used."),
    )

    links = StreamBlock(
        [
            ("link", MainMenuSubmenuLinkBlock()),
        ],
        label=_("Links"),
        max_num=8,
        required=False,
    )


TOP_MENU_BLOCKS = [
    ("link", MenuLinkWithIconBlock(label=_("Link"))),
]

FOOTER_BOTTOM_MENU_BLOCKS = [
    ("link", FooterBottomLinkBlock(label=_("Link"))),
]

MAIN_MENU_BLOCKS = [
    ("link", MainMenuLinkBlock(label=_("Link"))),
    ("submenu", MainMenuSubmenuBlock(label=_("Submenu"))),
]
