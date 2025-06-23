from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.template.context import Context
from django.utils.html import mark_safe
from wagtail.models import Site
from wagtail.rich_text import RichText

from sites_faciles.content_manager.models import MegaMenu

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


@register.simple_tag(takes_context=True)
def canonical_url(context):
    """
    Make the best effort to get a canonical URL for the current page, considering that:
    - Multiple schemes can be allowed (http vs https), but only one should be canonical
    - Sites can answer to multiple URLs, but only one should be canonical
    - Multiple sites can exist on the same instance
    - Some pages are not instances of Wagtail Pages (eg. search results, 404, etc.)
    """
    request = context.get("request", None)
    if not request:
        # For the error 500 page
        return ""

    scheme = settings.HOST_PROTO
    site = Site.find_for_request(request)

    if site:
        hostname = site.hostname
        if site.port != 80:
            hostname = f"{hostname}:{site.port}"
    else:
        hostname = request.get_host

    return f"{scheme}://{hostname}{request.path}"


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
        p["class"] = p.get("class", []) + [class_name]  # type: ignore

    return mark_safe(str(soup))


@register.simple_tag(takes_context=True)
def toggle_url_filter(context, *_, **kwargs):
    """
    Sets a URL filter, or removes it if it is already in use.

    The other filters can be passed through a dictionary or the GET parameters
    """

    filters_dict = kwargs.get("filters_dict", {})
    if filters_dict:
        url_params = filters_dict.copy()
    else:
        url_params = context["request"].GET.copy()

    filters = [("author", "id"), ("category", "slug"), ("source", "slug"), ("tag", "slug"), ("year", "")]

    for f in filters:
        param = f[0]
        attr = f[1]
        val = kwargs.get(param, "")
        current_val = context.get(f"current_{param}", "")

        if val and val != current_val:
            if attr:
                url_params[param] = getattr(val, attr)
            else:
                url_params[param] = val
        elif val and val == current_val:
            url_params.pop(param, None)

    url_string = "&".join(["{}={}".format(x[0], x[1]) for x in url_params.items()])

    if url_string:
        return f"?{url_string}"
    else:
        return ""


@register.filter
def table_has_heading_row(value):
    non_empty_heading = False
    for col in value:
        if col["heading"]:
            non_empty_heading = True
    return non_empty_heading
