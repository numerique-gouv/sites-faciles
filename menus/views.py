from wagtail.admin.viewsets.model import ModelViewSet, ModelViewSetGroup

from menus.models import FooterBottomMenu, MainMenu, TopMenu


class TopMenuViewSet(ModelViewSet):
    model = TopMenu
    icon = "minus"  # type: ignore


class FooterBottomMenuViewSet(ModelViewSet):
    model = FooterBottomMenu
    icon = "minus"  # type: ignore


class MainMenuViewSet(ModelViewSet):
    model = MainMenu
    icon = "minus"  # type: ignore


class MenusViewSetGroup(ModelViewSetGroup):
    items = (TopMenuViewSet, MainMenuViewSet, FooterBottomMenuViewSet)
    menu_icon = "bars"
    menu_label = "Menus"  # type: ignore
    menu_name = "menus"
    menu_order = 8400
