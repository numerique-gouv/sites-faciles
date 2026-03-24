from wagtail import hooks

from .views import MenusViewSetGroup


@hooks.register("register_admin_viewset")
def register_viewset():
    return MenusViewSetGroup()
