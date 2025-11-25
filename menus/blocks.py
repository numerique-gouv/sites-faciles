from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from wagtail.blocks import CharBlock, StreamBlock, StructBlock, StructValue

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


class MainMenuSubmenuStructValue(StructValue):
    def id(self):
        text = self.get("text", "")
        raw_id = slugify(text)
        return f"collapse-menu-{raw_id}"

    def menu_urls(self):
        links = self.get("links", [])

        urls = []
        for link in links:
            urls.append(link.value.url())

        return urls


class MainMenuSubmenuBlock(StructBlock):
    text = CharBlock(
        label=_("Submenu label"),
        required=True,
    )

    links = StreamBlock(
        [
            ("link", MainMenuSubmenuLinkBlock()),
        ],
        label=_("Links"),
        max_num=8,
        required=False,
    )

    class Meta:
        template = "menus/blocks/main_menu_submenu.html"
        value_class = MainMenuSubmenuStructValue


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
