from django import template
from django.conf import settings
from django.template.context import Context
from django.utils.html import SafeString, mark_safe
from wagtail.rich_text import RichText

from content_manager.models import MegaMenu


register = template.Library()


@register.inclusion_tag("content_manager/menus/mega_menu.html", takes_context=True)
def mega_menu(context: Context, parent_menu_id: int) -> dict:
    """
    Returns a mega_menu item. Takes the parent menu id as parameter,
    """
    menu = MegaMenu.objects.filter(parent_menu_item_id=parent_menu_id).first()

    return {"request": context["request"], "menu": menu}


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.filter
def richtext_p_add_class(value, class_name: str):
    """
    Adds a CSS class to a Richtext-generated paragraph.

    Intended to be used right after a `| richext` filter
    """

    if not class_name:
        raise ValueError("Missing or empty parameter: class_name.")

    if isinstance(value, RichText):
        # In case of a RichTextBlock, render it
        value = value.__html__()

    if isinstance(value, SafeString):
        # In case of a RichTextField, of after rendering a RichTextBlock
        return mark_safe(value.replace("<p data-block-key", f'<p class="{class_name}" data-block-key'))
    else:
        return value
