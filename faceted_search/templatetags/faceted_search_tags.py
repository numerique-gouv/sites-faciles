from django import template
from django.template.loader import render_to_string as _render_to_string

register = template.Library()


@register.simple_tag
def facet_label(name, count=None):
    """Label for a facet value tag, with result count when available.

    See ``faceted_search/result_counts.md`` for how ``count`` is computed.
    """
    if count is None or count == "":
        return str(name)
    return f"{name} ({count})"


@register.simple_tag
def facet_value(item, facet):
    """Value submitted by a facet checkbox: authors are selected by id, the rest by slug."""
    return item.pk if facet == "author" else item.slug


@register.simple_tag(takes_context=True)
def render_to_string(context, template_name, **kwargs):
    """Render a template to a string so it can be passed to inclusion tags."""
    new_context = context.flatten()
    new_context.update(kwargs)
    return _render_to_string(template_name, new_context, request=context.get("request"))
