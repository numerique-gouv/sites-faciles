from django.http import Http404
from django.views.generic import ListView
from wagtail.models import Page, Site

from faceted_search.facets import apply_facet_selection, get_facet_context, get_facet_selection_from_form
from faceted_search.forms import FacetedSearchForm
from faceted_search.search import RANK_BY_DATE, searchable_pages


class FacetedSearchResultsView(ListView):
    """Search with sidebar facets (collection, theme, tag, etc.).

    Template context (in addition to Django ``ListView`` defaults such as
    ``object_list``, ``page_obj``, ``paginator``, ``is_paginated``, ``view``):

    - ``form``: the bound :class:`~faceted_search.forms.FacetedSearchForm` holding
      every input of the page (search query, facet checkboxes, ranking).
    - ``query``: raw ``?q=`` string (or ``None``).
    - ``rank_by``: ``relevance`` (default) or ``date``.
    - Everything returned by :func:`faceted_search.facets.get_facet_context`
      (see its docstring).

    For doc on how result counts are computed, see ``faceted_search/result_counts.md``.
    """

    model = Page
    template_name = "faceted_search/search_results.html"
    paginate_by = 10

    def get_search_form(self):
        """Return the bound form, raising 404 for unknown facet values."""
        if not hasattr(self, "_search_form"):
            self.site = Site.find_for_request(self.request)
            form = FacetedSearchForm(self.request.GET, locale=self.site.root_page.localized.locale)
            if not form.is_valid():
                raise Http404(form.errors.as_text())
            self._search_form = form
        return self._search_form

    def get_queryset(self):
        form = self.get_search_form()
        query = form.cleaned_data["q"]
        if not query:
            return Page.objects.none()

        selection = get_facet_selection_from_form(form)
        rank_by = form.cleaned_data["rank_by"]
        pages = searchable_pages(self.request, self.site, rank_by=rank_by)
        object_list = apply_facet_selection(pages, self.site, selection)
        if rank_by == RANK_BY_DATE:
            # order_by_relevance=False is needed, from Wagtail docs.
            return object_list.order_by("-date").search(query, order_by_relevance=False)
        return object_list.search(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = self.get_search_form()
        context["form"] = form
        context["query"] = form.cleaned_data["q"] or None
        context["rank_by"] = form.cleaned_data["rank_by"]
        context.update(
            get_facet_context(
                self.request,
                selection=get_facet_selection_from_form(form),
                rank_by=context["rank_by"],
                query=context["query"],
            )
        )
        return context
