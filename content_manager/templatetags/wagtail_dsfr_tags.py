from django import template
from django.template.context import Context

from content_manager.models import MegaMenu


register = template.Library()


@register.inclusion_tag("content_manager/menus/mega_menu.html", takes_context=True)
def mega_menu(context: Context, parent_menu_id: int) -> dict:
    """
    Returns a mega_menu item. Takes the parent menu id as parameter,
    """
    menu = MegaMenu.objects.filter(parent_menu_item_id=parent_menu_id).first()

    return {"request": context["request"], "menu": menu}
