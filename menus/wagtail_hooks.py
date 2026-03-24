from wagtail import hooks

from menus.models import FooterBottomMenu, MainMenu, TopMenu

from .views import MenusViewSetGroup


@hooks.register("register_admin_viewset")
def register_viewset():
    return MenusViewSetGroup()


@hooks.register("construct_settings_menu")
def exclude_menus_from_settings_menu(request, menu_items):
    for index, item in enumerate(menu_items):
        try:
            if item.model in [TopMenu, FooterBottomMenu, MainMenu]:
                del menu_items[index]
        except AttributeError:
            # Prevent the loop to choke on some menu items that
            # do not specify model, like Redirect menu item
            pass
