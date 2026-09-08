"""Search facets (fork-specific; mirrors PublicationIndexPage and blog facets).

Result-count semantics for the sidebar are documented in ``faceted_search/result_counts.md``.
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from django.db.models import Count
from modelsearch.backends.base import BaseSearchResults
from wagtail.models import Site

from faceted_search.search import searchable_pages
from publications.models import Collection, PublicationPage, Theme
from sites_conformes.blog.models import BlogEntryPage, Category, Organization, Person
from sites_conformes.core.models import ContentPage, Tag

"""Which facet sections to show on the search page."""
ENABLED_FACETS: dict[str, bool] = {
    "category": False,
    "collection": True,
    "theme": True,
    "tag": True,
    "author": True,
    "source": True,
    "year": True,
}


@dataclass
class FacetSelection:
    categories: list[Category] = field(default_factory=list)
    collections: list[Collection] = field(default_factory=list)
    themes: list[Theme] = field(default_factory=list)
    tags: list[Tag] = field(default_factory=list)
    sources: list[Organization] = field(default_factory=list)
    authors: list[Person] = field(default_factory=list)
    years: list[str] = field(default_factory=list)


@dataclass
class FacetValueNode:
    value: Any
    children: list["FacetValueNode"] = field(default_factory=list)


def _build_facet_value_tree(taxonomies, taxonomy_model, locale) -> list[FacetValueNode]:
    """Build a tree containing selected taxonomies and all of their ancestors."""
    nodes = {taxonomy.pk: FacetValueNode(value=taxonomy) for taxonomy in taxonomies}

    missing = {taxonomy.parent_id for taxonomy in taxonomies if taxonomy.parent_id} - nodes.keys()
    while missing:
        for parent in taxonomy_model.objects.filter(locale=locale, id__in=missing).order_by("name"):
            nodes[parent.pk] = FacetValueNode(value=parent)
        missing = {node.value.parent_id for node in nodes.values() if node.value.parent_id} - nodes.keys()

    roots = []
    for node in sorted(nodes.values(), key=lambda item: item.value.name):
        parent_id = node.value.parent_id
        if parent_id in nodes:
            nodes[parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


def get_facet_selection_from_form(form) -> FacetSelection:
    """Resolve selected facet values from a validated ``FacetedSearchForm``."""
    data = form.cleaned_data
    return FacetSelection(
        categories=list(data["category"]),
        collections=list(data["collection"]),
        themes=list(data["theme"]),
        tags=list(data["tag"]),
        sources=list(data["source"]),
        authors=list(data["author"]),
        years=data["year"],
    )


def apply_facet_selection(queryset, site, selection: FacetSelection, *, exclude_facet: str | None = None):
    """Apply selected facet values to ``queryset``, optionally skipping one facet."""
    root = site.root_page.localized

    if selection.categories and exclude_facet != "category":
        matching_page_ids = (
            BlogEntryPage.objects.descendant_of(root)
            .live()
            .filter(blog_categories__in=selection.categories)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    if selection.collections and exclude_facet != "collection":
        matching_page_ids = (
            PublicationPage.objects.descendant_of(root)
            .live()
            .filter(collections__in=selection.collections)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    if selection.themes and exclude_facet != "theme":
        matching_page_ids = (
            PublicationPage.objects.descendant_of(root)
            .live()
            .filter(themes__in=selection.themes)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    if selection.tags and exclude_facet != "tag":
        content_page_ids = (
            ContentPage.objects.descendant_of(root).live().filter(tags__in=selection.tags).values_list("pk", flat=True)
        )
        blog_page_ids = (
            # PublicationPage entries are included (subclass of BlogEntryPage).
            BlogEntryPage.objects.descendant_of(root)
            .live()
            .filter(tags__in=selection.tags)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=content_page_ids.union(blog_page_ids))

    if selection.sources and exclude_facet != "source":
        matching_page_ids = (
            BlogEntryPage.objects.descendant_of(root)
            .live()
            .filter(authors__organization__in=selection.sources)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    if selection.authors and exclude_facet != "author":
        matching_page_ids = (
            BlogEntryPage.objects.descendant_of(root)
            .live()
            .filter(authors__in=selection.authors)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    if selection.years and exclude_facet != "year":
        matching_page_ids = (
            BlogEntryPage.objects.descendant_of(root)
            .live()
            .filter(date__year__in=selection.years)
            .values_list("pk", flat=True)
        )
        queryset = queryset.filter(pk__in=matching_page_ids)

    return queryset


def _page_pks_from_search_results(results: BaseSearchResults) -> list[int]:
    """Return primary keys from a Wagtail/modelsearch result set."""
    get_queryset = getattr(results, "get_queryset", None)
    if callable(get_queryset):
        return list(get_queryset().values_list("pk", flat=True))
    return [page.pk for page in results]


def _counts_for_m2m_field(model, page_ids: list[int], m2m_field_name: str) -> dict[int, int]:
    """Among ``page_ids``, count how many pages link to each related M2M object.

    For example::

        _counts_for_m2m_field(model=PublicationPage, page_ids=[101, 102, 103], m2m_field_name="themes")
        # → {7: 2, 9: 1}
        # theme 7 is on two of the three pages, theme 9 on one.

    Returns ``{m2m_object_pk: page_count}``

    Used for facets backed by a many-to-many (or parental M2M) on ``model``,
    e.g. ``PublicationPage.themes``.

    ``order_by()`` clears Page's default ``path`` ordering so it is not pulled
    into ``GROUP BY`` (which would otherwise cap every count at 1).
    """
    if not page_ids:
        return {}
    rows = (
        model.objects.filter(pk__in=page_ids)
        .order_by()
        .exclude(**{m2m_field_name: None})  # Exclude pages that don't have a value for the m2m field
        .values(m2m_field_name)  # Group by the m2m field
        .annotate(result_count=Count("pk", distinct=True))  # Count the number of pages for each m2m object
        .values_list(m2m_field_name, "result_count")  # Return the m2m object and the count
    )
    # rows is a list of (m2m_object_pk, count) tuples. Filter out None values.
    return {m2m_object_pk: count for m2m_object_pk, count in rows if m2m_object_pk is not None}


def _counts_for_tags(page_ids: list[int]) -> dict[int, int]:
    """Among ``page_ids``, count how many pages have each tag.

    Tags live on both ``ContentPage`` and ``BlogEntryPage`` (including
    publications), so both models are queried and the counts are merged.

    Returns ``{tag_pk: page_count}``, for example::

        _counts_for_tags([101, 102, 103])
        # → {4: 2, 8: 1} # tag 4 is on 2 pages, tag 8 is on 1 page
    """
    if not page_ids:
        return {}
    counter: Counter[int] = Counter()
    counter.update(ContentPage.objects.filter(pk__in=page_ids).order_by().values_list("tags", flat=True))
    counter.update(BlogEntryPage.objects.filter(pk__in=page_ids).order_by().values_list("tags", flat=True))
    counter.pop(None, None)
    return dict(counter)


def _counts_for_sources(page_ids: list[int]) -> dict[int, int]:
    """Among ``page_ids``, count how many pages have each source organization.

    Sources are not a direct M2M on the page: they are reached via
    ``BlogEntryPage.authors__organization``.

    Returns ``{organization_pk: page_count}``, for example::

        _counts_for_sources([101, 102, 103])
        # → {2: 2, 5: 1} # organization 2 is on 2 pages, organization 5 is on 1 page
    """
    if not page_ids:
        return {}
    rows = (
        BlogEntryPage.objects.filter(pk__in=page_ids)
        .order_by()
        .exclude(authors__organization=None)
        .values("authors__organization")
        .annotate(result_count=Count("pk", distinct=True))
        .values_list("authors__organization", "result_count")
    )
    return {pk: count for pk, count in rows if pk is not None}


def _search_without_given_facet(
    request, site, query: str, selection: FacetSelection, facet: str, *, rank_by: str
) -> BaseSearchResults:
    """Full-text search with all selected facet values except ``facet``."""
    queryset = apply_facet_selection(
        searchable_pages(request, site, rank_by=rank_by), site, selection, exclude_facet=facet
    )
    return queryset.search(query)


def compute_facet_result_counts(
    request,
    site,
    query: str,
    selection: FacetSelection,
    *,
    enabled_facets: dict[str, bool],
    rank_by: str,
) -> dict[str, dict[int, int]]:
    """Compute sidebar result counts for each enabled facet value.

    Returns ``{facet_name: {object_pk: count}}``, for example::

        {
        "theme": {7: 12, 9: 3}, # "theme 7 (12)", "theme 9 (3)"
        "tag": ...
        }

    See ``faceted_search/result_counts.md`` for how the counts are computed, with examples.
    """
    counts: dict[str, dict[int, int]] = {}

    if enabled_facets.get("category"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "category", rank_by=rank_by)
        )
        counts["category"] = _counts_for_m2m_field(BlogEntryPage, page_ids, "blog_categories")

    if enabled_facets.get("collection"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "collection", rank_by=rank_by)
        )
        counts["collection"] = _counts_for_m2m_field(PublicationPage, page_ids, "collections")

    if enabled_facets.get("theme"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "theme", rank_by=rank_by)
        )
        counts["theme"] = _counts_for_m2m_field(PublicationPage, page_ids, "themes")

    if enabled_facets.get("tag"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "tag", rank_by=rank_by)
        )
        counts["tag"] = _counts_for_tags(page_ids)

    if enabled_facets.get("author"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "author", rank_by=rank_by)
        )
        counts["author"] = _counts_for_m2m_field(BlogEntryPage, page_ids, "authors")

    if enabled_facets.get("source"):
        page_ids = _page_pks_from_search_results(
            _search_without_given_facet(request, site, query, selection, "source", rank_by=rank_by)
        )
        counts["source"] = _counts_for_sources(page_ids)

    return counts


def _set_result_counts(items, counts_by_pk: dict[int, int]) -> None:
    """Set ``result_count`` on each item from ``counts_by_pk`` (0 if missing)."""
    for item in items:
        item.result_count = counts_by_pk.get(item.pk, 0)


def _drop_zeroes(items, *, selected=()) -> list:
    """Keep items with ``result_count > 0``, plus any currently selected values."""
    return [item for item in items if item.result_count > 0 or item in selected]


def _facet_values_with_counts_or_selected(taxonomy_model, locale, counts_by_pk: dict[int, int], selected) -> list:
    """Facet values with a positive result count or currently selected (for tree building)."""
    selected_pks = {item.pk for item in selected}
    keep_pks = {pk for pk, count in counts_by_pk.items() if count > 0} | selected_pks
    taxonomies = list(taxonomy_model.objects.filter(locale=locale, id__in=keep_pks).order_by("name"))
    _set_result_counts(taxonomies, counts_by_pk)
    return taxonomies


def _attach_counts_to_tree(nodes, counts_by_pk: dict[int, int]) -> None:
    for node in nodes:
        _set_result_counts((node.value,), counts_by_pk)
        _attach_counts_to_tree(node.children, counts_by_pk)


def _facet_value_tree(
    taxonomy_model,
    locale,
    *,
    related_ids,
    counts_by_pk: dict[int, int] | None = None,
    selected=(),
) -> list[FacetValueNode]:
    """Build a collection/theme facet-value tree, optionally scoped by result counts."""
    if counts_by_pk is not None:
        taxonomies = _facet_values_with_counts_or_selected(taxonomy_model, locale, counts_by_pk, selected)
        tree = _build_facet_value_tree(taxonomies, taxonomy_model, locale)
        _attach_counts_to_tree(tree, counts_by_pk)
        return tree
    taxonomies = taxonomy_model.objects.filter(locale=locale, id__in=related_ids).order_by("name")
    return _build_facet_value_tree(taxonomies, taxonomy_model, locale)


def _set_facet_selection_result_counts(selection: FacetSelection, facet_counts: dict[str, dict[int, int]]) -> None:
    """Attach result counts to selected facet values (sidebar chips)."""
    _set_result_counts(selection.categories, facet_counts.get("category", {}))
    _set_result_counts(selection.collections, facet_counts.get("collection", {}))
    _set_result_counts(selection.themes, facet_counts.get("theme", {}))
    _set_result_counts(selection.tags, facet_counts.get("tag", {}))
    _set_result_counts(selection.sources, facet_counts.get("source", {}))
    _set_result_counts(selection.authors, facet_counts.get("author", {}))


def get_facet_context(
    request,
    *,
    selection: FacetSelection,
    rank_by: str,
    enabled_facets: dict[str, bool] | None = None,
    query: str | None = None,
) -> dict:
    """Build context for the facet sidebar.

    ``selection`` holds the facet values selected by the user, and ``rank_by`` the
    chosen ranking, both as validated by
    :class:`~faceted_search.forms.FacetedSearchForm`. ``rank_by`` is needed because
    result counts follow ``searchable_pages``, whose page types depend on it.

    Always present
    --------------
    - ``enabled_facets``: ``dict[str, bool]`` of which facets are enabled.
    - ``selected_*``: ``list[T]`` for each selected facet value.
    - ``selected_years``: ``list[str]`` selected via ``?year=`` (valid YYYY only).
      There is no year option list in the sidebar yet; years are only applied
      as selected facet values when present in the URL.
    - ``show_search_facets``: ``bool``, true when at least one enabled facet
      has options to display.

    Present only when the matching ``enabled_facets`` flag is true
    --------------------------------------------------------------
    - ``categories``: ``list[Category]`` (flat).
    - ``tags``: ``list[Tag]`` (flat).
    - ``authors``: ``list[Person]`` (flat).
    - ``sources``: ``list[Organization]`` (flat).
    - ``collection_tree``: ``list[FacetValueNode]`` (hierarchical).
    - ``theme_tree``: ``list[FacetValueNode]`` (hierarchical).

    When ``query`` is set (search page with ``?q=``)
    -----------------------------------------------
    Result counts are attached as ``result_count`` (``int``) on:

    - each item in ``categories`` / ``tags`` / ``authors`` / ``sources``;
    - each ``node.value`` in ``collection_tree`` / ``theme_tree``;
    - each object in the corresponding ``selected_*`` lists (for selected chips).

    Unselected options with ``result_count == 0`` are omitted from the option
    lists/trees; selected values are kept. How counts are computed is described
    in ``faceted_search/result_counts.md``.

    When ``query`` is omitted, option lists are built from all live content
    under the site root (no ``result_count``, zeroes not filtered out).

    Example
    -------
    Request ``/search/?q=blé&theme=agriculture&author=42`` with only theme and
    author facets enabled::

        theme = Theme(name="Agriculture")
        theme.result_count = 12
        author = Person(name="Ada")
        author.result_count = 5

        {
            "enabled_facets": {"theme": True, "author": True, ...},
            "selected_themes": [theme],    # theme.result_count == 12
            "selected_authors": [author],  # author.result_count == 5
            "theme_tree": [
                FacetValueNode(value=theme, children=[]),
            ],
            "authors": [author],          # author.result_count == 5
            "show_search_facets": True,
            # …other enabled_facets / selected_* keys omitted here for brevity
        }
    """
    if enabled_facets is None:
        enabled_facets = ENABLED_FACETS

    site = Site.find_for_request(request)

    facet_counts: dict[str, dict[int, int]] = {}
    if query:
        facet_counts = compute_facet_result_counts(
            request, site, query, selection, enabled_facets=enabled_facets, rank_by=rank_by
        )

    context = {
        "enabled_facets": enabled_facets,
        "selected_years": selection.years,
    }

    root = site.root_page.localized
    locale = root.locale
    # Includes PublicationPage entries (subclass of BlogEntryPage).
    blog_entries = BlogEntryPage.objects.descendant_of(root).live()
    content_pages = ContentPage.objects.descendant_of(root).live()
    publication_pages = PublicationPage.objects.descendant_of(root).live()

    if enabled_facets.get("category"):
        category_ids = blog_entries.values_list("blog_categories", flat=True)
        categories = list(Category.objects.filter(id__in=category_ids, locale=locale).order_by("name"))
        if query:
            category_counts = facet_counts.get("category", {})
            _set_result_counts(categories, category_counts)
            categories = _drop_zeroes(categories, selected=selection.categories)
        context["categories"] = categories

    if enabled_facets.get("tag"):
        tag_ids = set(content_pages.values_list("tags", flat=True))
        tag_ids |= set(blog_entries.values_list("tags", flat=True))
        tag_ids.discard(None)
        tags = list(Tag.objects.filter(id__in=tag_ids).order_by("name"))
        if query:
            tag_counts = facet_counts.get("tag", {})
            _set_result_counts(tags, tag_counts)
            tags = _drop_zeroes(tags, selected=selection.tags)
        context["tags"] = tags

    if enabled_facets.get("author"):
        author_ids = blog_entries.values_list("authors", flat=True)
        authors = list(Person.objects.filter(id__in=author_ids).order_by("name"))
        if query:
            author_counts = facet_counts.get("author", {})
            _set_result_counts(authors, author_counts)
            authors = _drop_zeroes(authors, selected=selection.authors)
        context["authors"] = authors

    if enabled_facets.get("source"):
        org_ids = blog_entries.values_list("authors__organization", flat=True)
        sources = list(Organization.objects.filter(id__in=org_ids).order_by("name"))
        if query:
            source_counts = facet_counts.get("source", {})
            _set_result_counts(sources, source_counts)
            sources = _drop_zeroes(sources, selected=selection.sources)
        context["sources"] = sources

    if enabled_facets.get("collection"):
        context["collection_tree"] = _facet_value_tree(
            Collection,
            locale,
            related_ids=publication_pages.values_list("collections", flat=True),
            counts_by_pk=facet_counts.get("collection") if query else None,
            selected=selection.collections,
        )

    if enabled_facets.get("theme"):
        context["theme_tree"] = _facet_value_tree(
            Theme,
            locale,
            related_ids=publication_pages.values_list("themes", flat=True),
            counts_by_pk=facet_counts.get("theme") if query else None,
            selected=selection.themes,
        )

    if query:
        _set_facet_selection_result_counts(selection, facet_counts)

    context["selected_categories"] = selection.categories
    context["selected_collections"] = selection.collections
    context["selected_themes"] = selection.themes
    context["selected_tags"] = selection.tags
    context["selected_sources"] = selection.sources
    context["selected_authors"] = selection.authors

    context["show_search_facets"] = _show_search_facets(context)
    return context


def _show_search_facets(context: dict) -> bool:
    enabled = context.get("enabled_facets") or {}
    if enabled.get("category") and context.get("categories"):
        return True
    if enabled.get("collection") and context.get("collection_tree"):
        return True
    if enabled.get("theme") and context.get("theme_tree"):
        return True
    if enabled.get("tag") and context.get("tags"):
        return True
    if enabled.get("author") and context.get("authors"):
        return True
    if enabled.get("source") and context.get("sources"):
        return True
    return False
