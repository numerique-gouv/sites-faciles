from wagtail.models import Page

from sites_conformes.blog.models import BlogEntryPage

RANK_BY_RELEVANCE = "relevance"
RANK_BY_DATE = "date"


def searchable_pages(request, site, *, rank_by: str):
    """Live pages under the site root, restricted to public pages for anonymous users.

    When ``rank_by`` is ``date``, only ``BlogEntryPage`` (and subclasses) are included,
    since ContentPages have no editorial date. ``rank_by`` comes from
    :class:`~faceted_search.forms.FacetedSearchForm`, which owns its validation and default.
    """
    root = site.root_page.localized
    queryset = Page.objects.descendant_of(root, inclusive=True).live()
    if not request.user.is_authenticated:
        queryset = queryset.public()
    if rank_by == RANK_BY_DATE:
        return BlogEntryPage.objects.filter(pk__in=queryset)  # includes PublicationPages (subclass of BlogEntryPage)
    return queryset
