from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.template.context import Context
from django.utils.html import mark_safe
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

    Intended to be used right after a `| richext` filter in case of a RichTextField
    (not necessary for a RichTextBlock)
    """

    if not class_name:
        return value

    if isinstance(value, RichText):
        # In case of a RichTextBlock, first render it
        value = str(value)

    soup = BeautifulSoup(value, "html.parser")

    paragraphs = soup.find_all("p")

    for p in paragraphs:
        p["class"] = p.get("class", []) + [class_name]

    return mark_safe(str(soup))


@register.simple_tag(takes_context=True)
def toggle_url_filter(context, *_, **kwargs):
    """
    Sets a singular URL filter, or removes it if it is already in use.
    """
    url_string = ""

    author = kwargs.get("author", "")
    current_author = context.get("current_author", "")
    if author and author != current_author:
        url_string = f"?author={author.id}"

    category = kwargs.get("category", "")
    current_category = context.get("current_category", "")
    if category and category != current_category:
        url_string = f"?category={category.slug}"

    source = kwargs.get("source", "")
    current_source = context.get("current_source", "")
    if source and source != current_source:
        url_string = f"?source={source.slug}"

    tag = kwargs.get("tag", "")
    current_tag = context.get("current_tag", "")
    if tag and tag != current_tag:
        url_string = f"?tag={tag.slug}"

    return url_string
