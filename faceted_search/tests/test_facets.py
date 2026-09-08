"""Faceted search filter tests.

Structured like ``publications.tests.test_publication_index_page``: shared filter
cases drive result filtering, sidebar visibility, and combination behaviour.

Blog-specific filters (e.g. category) are not covered here: this project uses
publications, not a standalone blog.
"""

import zoneinfo
from datetime import datetime
from itertools import combinations
from pathlib import Path
from urllib.parse import urlencode

import dsfr
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase

from faceted_search.facets import (
    ENABLED_FACETS,
    FacetSelection,
    compute_facet_result_counts,
    get_facet_context,
    get_facet_selection_from_form,
)
from faceted_search.forms import FacetedSearchForm
from faceted_search.search import RANK_BY_RELEVANCE
from faceted_search.views import FacetedSearchResultsView
from publications.tests.factories import (
    CollectionFactory,
    PublicationIndexPageFactory,
    PublicationPageFactory,
    ThemeFactory,
)
from publications.tests.test_publication_index_page import PublicationIndexPageFilterTestBase
from sites_conformes.blog.tests.factories import TagFactory
from sites_conformes.core.models import ContentPage
from sites_conformes.core.search_view_loader import get_search_results_view

FILTER_CASES = [
    {
        "name": "collection",
        "relation": "collections",
    },
    {
        "name": "theme",
        "relation": "themes",
    },
    {
        "name": "tag",
        "relation": "tags",
    },
]


def _all_facets_disabled() -> dict[str, bool]:
    return dict.fromkeys(ENABLED_FACETS, False)


def validated_form_for(request, site) -> FacetedSearchForm:
    """Bind and validate the search form the way the view does."""
    form = FacetedSearchForm(request.GET, locale=site.root_page.localized.locale)
    if not form.is_valid():
        raise Http404(form.errors.as_text())
    return form


def facet_selection_for(request, site) -> FacetSelection:
    """Resolve the facet selection of a request the way the view does."""
    return get_facet_selection_from_form(validated_form_for(request, site))


def get_post_titles_in_response(response) -> list[str]:
    return [
        link.get_text(strip=True)
        for link in BeautifulSoup(response.content, "html.parser").select("#search-results ol a")
    ]


class FacetedSearchTestBase(PublicationIndexPageFilterTestBase):
    filter_cases = FILTER_CASES
    search_query = "Post"

    def search_url(self, query=None, **params):
        query = self.search_query if query is None else query
        url = reverse("cms_search")
        return f"{url}?{urlencode({'q': query, **params}, doseq=True)}"

    def search_request(self, query=None, **params):
        """Build a GET request for the search URL without rendering the view."""
        request = RequestFactory().get(self.search_url(query=query, **params))
        request.user = AnonymousUser()
        return request


class FacetedSearchViewRegistrationTest(SimpleTestCase):
    def test_faceted_search_registers_its_view(self):
        self.assertIs(get_search_results_view().view_class, FacetedSearchResultsView)


class FacetedSearchRegistrationTest(FacetedSearchTestBase):
    def test_search_uses_faceted_template(self):
        response = self.client.get(self.search_url())
        template_names = [template.name for template in response.templates]
        self.assertIn("faceted_search/search_results.html", template_names)


class FacetedSearchContextTest(FacetedSearchTestBase):
    """Test that``get_facet_context`` builds sidebar lists according to ``enabled_facets``.
    We use a dummy request rather than a real client request, to save test running time."""

    def test_enabled_filter_flags_populate_context_lists(self):
        """Test that when a given filter is enabled, the context also has the filter activated,
        and it includes the taxonomy item for that filter."""
        request = RequestFactory().get("/")

        def tree_nodes(tree):
            for node in tree:
                yield node.value
                yield from tree_nodes(node.children)

        for case in self.filter_cases:
            facet = case["name"]
            expected_item = getattr(self, facet)
            enabled_flags = {**_all_facets_disabled(), facet: True}

            with self.subTest(facet):
                context = get_facet_context(
                    request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=enabled_flags
                )
                self.assertTrue(context["enabled_facets"][facet])
                if facet in ("collection", "theme"):
                    self.assertIn(expected_item, list(tree_nodes(context[f"{facet}_tree"])))
                else:
                    self.assertIn(expected_item, list(context[f"{facet}s"]))

        with self.subTest("author"):
            enabled_flags = {**_all_facets_disabled(), "author": True}
            context = get_facet_context(
                request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=enabled_flags
            )
            self.assertTrue(context["enabled_facets"]["author"])
            self.assertIn(self.author, list(context["authors"]))

        with self.subTest("source"):
            enabled_flags = {**_all_facets_disabled(), "source": True}
            context = get_facet_context(
                request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=enabled_flags
            )
            self.assertTrue(context["enabled_facets"]["source"])
            self.assertIn(self.organization, list(context["sources"]))

    def test_collection_and_theme_filter_context_is_hierarchical(self):
        parent_collection = CollectionFactory(locale=self.index.locale, name="Parent collection")
        child_collection = CollectionFactory(
            locale=self.index.locale,
            name="Child collection",
            parent=parent_collection,
        )
        parent_theme = ThemeFactory(locale=self.index.locale, name="Parent theme")
        child_theme = ThemeFactory(locale=self.index.locale, name="Child theme", parent=parent_theme)
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            collections=[child_collection],
            themes=[child_theme],
        )
        request = RequestFactory().get("/")
        context = get_facet_context(request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE)

        collection_parent = next(node for node in context["collection_tree"] if node.value == parent_collection)
        theme_parent = next(node for node in context["theme_tree"] if node.value == parent_theme)
        self.assertEqual([node.value for node in collection_parent.children], [child_collection])
        self.assertEqual([node.value for node in theme_parent.children], [child_theme])

    def test_disabled_filter_flags_omit_context_lists(self):
        request = RequestFactory().get("/")
        context = get_facet_context(
            request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=_all_facets_disabled()
        )

        for case in self.filter_cases:
            facet = case["name"]

            with self.subTest(facet):
                self.assertFalse(context["enabled_facets"][facet])
                self.assertNotIn(f"{facet}s", context)

        self.assertFalse(context["enabled_facets"]["author"])
        self.assertNotIn("authors", context)
        self.assertFalse(context["enabled_facets"]["source"])
        self.assertNotIn("sources", context)

    def test_show_search_facets_follows_enabled_flags(self):
        request = RequestFactory().get("/")
        enabled_flags = {**_all_facets_disabled(), "collection": True}
        context = get_facet_context(
            request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=enabled_flags
        )
        self.assertTrue(context["show_search_facets"])

        context = get_facet_context(
            request, selection=FacetSelection(), rank_by=RANK_BY_RELEVANCE, enabled_facets=_all_facets_disabled()
        )
        self.assertFalse(context["show_search_facets"])


class FacetedSearchQueryTest(FacetedSearchTestBase):
    """Full-text search combined with facet filters (``facet_before_search``).
    Posts should match the search query and the given filter. Other combinations should not match."""

    def test_single_filter_single_value(self):
        for case in self.filter_cases:
            facet = case["name"]
            taxonomy = getattr(self, facet)
            filtered_url = self.search_url(**{facet: taxonomy.slug})
            matching_post_title = getattr(self, f"post_with_{facet}").title
            other_post_title = getattr(self, f"post_with_other_{facet}").title

            with self.subTest(facet):
                post_without_search_match = self.entry_page_factory(
                    parent=self.index,
                    owner=self.admin,
                    title="Annual Report",
                    slug=f"annual-report-no-search-match-{facet}",
                    **{case["relation"]: [taxonomy]},
                )
                response = self.client.get(filtered_url)
                self.assertEqual(response.status_code, 200)
                post_titles = get_post_titles_in_response(response)
                self.assertIn(matching_post_title, post_titles)
                self.assertNotIn(other_post_title, post_titles)
                self.assertNotIn(post_without_search_match.title, post_titles)

    def test_single_filter_multiple_values(self):
        for case in self.filter_cases:
            facet = case["name"]
            taxonomy = getattr(self, facet)
            other_taxonomy = getattr(self, f"other_{facet}")

            with self.subTest(facet):
                post_without_search_match = self.entry_page_factory(
                    parent=self.index,
                    owner=self.admin,
                    title="Annual Report",
                    slug=f"annual-report-no-search-match-{facet}-multiple",
                    **{case["relation"]: [taxonomy, other_taxonomy]},
                )
                response = self.client.get(self.search_url(**{facet: [taxonomy.slug, other_taxonomy.slug]}))
                self.assertEqual(response.status_code, 200)
                post_titles = get_post_titles_in_response(response)
                self.assertIn(getattr(self, f"post_with_{facet}").title, post_titles)
                self.assertIn(getattr(self, f"post_with_other_{facet}").title, post_titles)
                self.assertNotIn(post_without_search_match.title, post_titles)

    def test_author_filter_single_value(self):
        post_without_search_match = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Annual Report",
            slug="annual-report-no-search-match-author",
            authors=[self.author],
        )
        response = self.client.get(self.search_url(author=self.author.id))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_author.title, post_titles)
        self.assertNotIn(self.post_with_other_author.title, post_titles)
        self.assertNotIn(post_without_search_match.title, post_titles)

    def test_author_filter_multiple_values(self):
        response = self.client.get(self.search_url(author=[self.author.id, self.other_author.id]))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_author.title, post_titles)
        self.assertIn(self.post_with_other_author.title, post_titles)

    def test_source_filter_single_value(self):
        post_without_search_match = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Annual Report",
            slug="annual-report-no-search-match-source",
            authors=[self.author],
        )
        response = self.client.get(self.search_url(source=self.organization.slug))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_author.title, post_titles)
        self.assertNotIn(self.post_with_other_author.title, post_titles)
        self.assertNotIn(post_without_search_match.title, post_titles)

    def test_source_filter_multiple_values(self):
        response = self.client.get(self.search_url(source=[self.organization.slug, self.other_organization.slug]))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_author.title, post_titles)
        self.assertIn(self.post_with_other_author.title, post_titles)

    def test_invalid_filter_value_returns_404(self):
        response = self.client.get(self.search_url(collection="nonexistent"))
        self.assertEqual(response.status_code, 404)

    def test_invalid_filter_multiple_values_returns_404(self):
        response = self.client.get(self.search_url(collection=[self.collection.slug, "nonexistent"]))
        self.assertEqual(response.status_code, 404)

    def test_invalid_author_id_returns_404(self):
        response = self.client.get(self.search_url(author="not-an-id"))
        self.assertEqual(response.status_code, 404)

    def test_invalid_year_is_ignored(self):
        response = self.client.get(self.search_url(year="not-a-year"))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_collection.title, post_titles)
        self.assertIn(self.post_with_theme.title, post_titles)

    def test_year_filter_filters_by_year(self):
        post_from_other_year = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post from 2023",
            slug="post-from-2023",
            date=datetime(2023, 1, 1, 12, 0, 0, tzinfo=zoneinfo.ZoneInfo("Europe/Paris")),
        )
        response = self.client.get(self.search_url(year=2024))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(self.post_with_collection.title, post_titles)
        self.assertIn(self.post_with_theme.title, post_titles)
        self.assertNotIn(post_from_other_year.title, post_titles)

    def test_uses_OR_within_filter(self):
        """Test that multiple values within a single filter use OR semantics."""
        response = self.client.get(self.search_url(collection=[self.collection.slug, self.other_collection.slug]))
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        """Test that posts that match any of the values are included in the results."""
        self.assertIn(self.post_with_collection.title, post_titles)
        self.assertIn(self.post_with_other_collection.title, post_titles)

    def test_uses_AND_across_filters(self):
        """Test that multiple values across filters use AND semantics."""
        matching = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            collections=[self.collection],
            themes=[self.theme],
        )
        response = self.client.get(
            self.search_url(
                collection=[self.collection.slug, self.other_collection.slug],
                theme=[self.theme.slug, self.other_theme.slug],
            )
        )
        self.assertEqual(response.status_code, 200)
        post_titles = get_post_titles_in_response(response)
        self.assertIn(matching.title, post_titles)
        """Test that posts that match only one filter are not included in the results."""
        self.assertNotIn(self.post_with_collection.title, post_titles)
        self.assertNotIn(self.post_with_theme.title, post_titles)


class FacetedSearchCombinationTest(FacetedSearchTestBase):
    """Test that two filters can be combined in the search URL."""

    def test_two_filters_single_value(self):
        for case_a, case_b in combinations(self.filter_cases, 2):
            facet_a = case_a["name"]
            facet_b = case_b["name"]
            search_params = {
                facet_a: getattr(self, facet_a).slug,
                facet_b: getattr(self, facet_b).slug,
            }
            post_kwargs = {
                case_a["relation"]: [getattr(self, facet_a)],
                case_b["relation"]: [getattr(self, facet_b)],
            }

            with self.subTest(f"{facet_a}+{facet_b}"):
                matching = self.entry_page_factory(parent=self.index, owner=self.admin, **post_kwargs)
                post_without_search_match = self.entry_page_factory(
                    parent=self.index,
                    owner=self.admin,
                    title="Annual Report",
                    slug=f"annual-report-no-search-match-{facet_a}-{facet_b}",
                    **post_kwargs,
                )
                response = self.client.get(self.search_url(**search_params))
                post_titles = get_post_titles_in_response(response)
                self.assertIn(matching.title, post_titles)
                self.assertNotIn(post_without_search_match.title, post_titles)
                for case in (case_a, case_b):
                    """Test that posts that match only one filter are not included in the results."""
                    case_name = case["name"]
                    self.assertNotIn(getattr(self, f"post_with_{case_name}").title, post_titles)
                    self.assertNotIn(getattr(self, f"post_with_other_{case_name}").title, post_titles)

    def test_two_filters_multiple_values(self):
        # Example: facet_a="collection", values_a=[self.collection, self.other_collection],
        # facet_b="theme", values_b=[self.theme, self.other_theme].
        for case_a, case_b in combinations(self.filter_cases, 2):
            facet_a = case_a["name"]
            facet_b = case_b["name"]
            values_a = [getattr(self, facet_a), getattr(self, f"other_{facet_a}")]
            values_b = [getattr(self, facet_b), getattr(self, f"other_{facet_b}")]
            matching = self.entry_page_factory(
                parent=self.index,
                owner=self.admin,
                **{
                    case_a["relation"]: values_a,
                    case_b["relation"]: values_b,
                },
            )
            post_without_search_match = self.entry_page_factory(
                parent=self.index,
                owner=self.admin,
                title="Annual Report",
                slug=f"annual-report-no-search-match-{facet_a}-{facet_b}-multiple",
                **{
                    case_a["relation"]: values_a,
                    case_b["relation"]: values_b,
                },
            )
            response = self.client.get(
                self.search_url(
                    **{
                        facet_a: [taxonomy.slug for taxonomy in values_a],
                        facet_b: [taxonomy.slug for taxonomy in values_b],
                    }
                )
            )
            self.assertEqual(response.status_code, 200)
            post_titles = get_post_titles_in_response(response)
            self.assertIn(matching.title, post_titles)
            self.assertNotIn(post_without_search_match.title, post_titles)
            """ Test that posts that match only one filter are not included in the results."""
            self.assertNotIn(getattr(self, f"post_with_{facet_a}").title, post_titles)
            self.assertNotIn(getattr(self, f"post_with_other_{facet_a}").title, post_titles)
            self.assertNotIn(getattr(self, f"post_with_{facet_b}").title, post_titles)
            self.assertNotIn(getattr(self, f"post_with_other_{facet_b}").title, post_titles)


class FacetedSearchGetFacetSelectionTest(FacetedSearchTestBase):
    """Test the facet selection resolved from the search form.
    We use a dummy request rather than a real client request, to save test running time."""

    def test_get_facet_selection_from_request__single_value(self):
        request = RequestFactory().get("/", {"collection": self.collection.slug, "tag": self.tag.slug})
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        self.assertEqual(selection.collections, [self.collection])
        self.assertEqual(selection.tags, [self.tag])

    def test_get_facet_selection_from_request__multiple_values(self):
        request = RequestFactory().get("/", {"collection": [self.collection.slug, self.other_collection.slug]})
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        self.assertEqual(selection.collections, [self.collection, self.other_collection])

    def test_get_facet_selection_from_request__invalid_author_id_raises_404(self):
        request = RequestFactory().get("/", {"author": "not-an-id"})
        site = Site.objects.get(is_default_site=True)
        with self.assertRaises(Http404):
            facet_selection_for(request, site)

    def test_get_facet_selection_from_request__invalid_year_is_ignored(self):
        request = RequestFactory().get("/", {"year": ["2024", "not-a-year", "23"]})
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        self.assertEqual(selection.years, ["2024"])


def _tree_taxonomies(nodes):
    for node in nodes:
        yield node.value
        yield from _tree_taxonomies(node.children)


class FacetedSearchCountComputingTest(FacetedSearchTestBase):
    """``result_count(V in F) = |q ∧ other facets ∧ F={V} only|``.

    See ``faceted_search/result_counts.md``. Shared M2M facets use one semantic
    case; tags/sources get thin smokes for their unique aggregators.
    We use a dummy request rather than a real client request, to save test running time.
    """

    def test_aggregation_can_exceed_one_per_value(self):
        """Page.ordering by path must not collapse GROUP BY aggregations to 1."""
        for index in range(3):
            self.entry_page_factory(
                parent=self.index,
                owner=self.admin,
                title=f"Post shared theme {index}",
                slug=f"post-shared-theme-{index}",
                themes=[self.theme],
            )
        request = self.search_request()  # no selected facets
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        counts = compute_facet_result_counts(
            request,
            site,
            self.search_query,
            selection,
            rank_by=RANK_BY_RELEVANCE,
            enabled_facets={**_all_facets_disabled(), "theme": True},
        )
        # fixture post_with_theme + 3 new posts
        self.assertGreaterEqual(counts["theme"].get(self.theme.pk), 4)

    def test_respects_other_facets_and_ignores_same_facet(self):
        # collection A + theme T
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post result count A T",
            slug="post-result-count-a-t",
            collections=[self.collection],
            themes=[self.theme],
        )
        # collection B + theme T
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post result count B T",
            slug="post-result-count-b-t",
            collections=[self.other_collection],
            themes=[self.theme],
        )
        # collection A + other theme
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post result count A other theme",
            slug="post-result-count-a-other-theme",
            collections=[self.collection],
            themes=[self.other_theme],
        )
        # selected: theme=T, collection=A
        request = self.search_request(theme=self.theme.slug, collection=self.collection.slug)
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        counts = compute_facet_result_counts(
            request,
            site,
            self.search_query,
            selection,
            rank_by=RANK_BY_RELEVANCE,
            enabled_facets={**_all_facets_disabled(), "collection": True, "theme": True},
        )

        # Theme facet ignores selected theme; keeps collection=A → posts with A (theme T and other)
        self.assertEqual(counts["theme"].get(self.theme.pk), 1)
        self.assertEqual(counts["theme"].get(self.other_theme.pk), 1)
        # Collection facet ignores selected collection; keeps theme=T → A and B both count
        self.assertEqual(counts["collection"].get(self.collection.pk), 1)
        self.assertEqual(counts["collection"].get(self.other_collection.pk), 1)

    def test_tags_counts(self):
        """``_counts_for_tags`` path (not shared M2M helper)."""
        for index in range(2):
            self.entry_page_factory(
                parent=self.index,
                owner=self.admin,
                title=f"Post tag count {index}",
                slug=f"post-tag-count-{index}",
                tags=[self.tag],
            )
        request = self.search_request()
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        counts = compute_facet_result_counts(
            request,
            site,
            self.search_query,
            selection,
            rank_by=RANK_BY_RELEVANCE,
            enabled_facets={**_all_facets_disabled(), "tag": True},
        )
        # fixture post_with_tag + 2 new posts
        self.assertEqual(counts["tag"].get(self.tag.pk), 3)

    def test_sources_count(self):
        """``_counts_for_sources`` path (authors__organization)."""
        for index in range(2):
            self.entry_page_factory(
                parent=self.index,
                owner=self.admin,
                title=f"Post source count {index}",
                slug=f"post-source-count-{index}",
                authors=[self.author],
            )
        request = self.search_request()
        site = Site.objects.get(is_default_site=True)
        selection = facet_selection_for(request, site)
        counts = compute_facet_result_counts(
            request,
            site,
            self.search_query,
            selection,
            rank_by=RANK_BY_RELEVANCE,
            enabled_facets={**_all_facets_disabled(), "source": True},
        )
        # fixture post_with_author + 2 new posts
        self.assertEqual(counts["source"].get(self.organization.pk), 3)


class FacetedSearchCountZeroesTest(FacetedSearchTestBase):
    """With ``query``, hide unselected zeroes; keep selected zeroes."""

    def test_hides_unselected_zeroes(self):
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post count context",
            slug="post-count-context",
            collections=[self.collection],
            themes=[self.theme],
        )
        request = self.search_request(theme=self.theme.slug)
        site = Site.objects.get(is_default_site=True)
        context = get_facet_context(
            request,
            selection=facet_selection_for(request, site),
            rank_by=RANK_BY_RELEVANCE,
            query=self.search_query,
            enabled_facets={**_all_facets_disabled(), "collection": True, "theme": True},
        )

        collection_pks = {taxonomy.pk for taxonomy in _tree_taxonomies(context["collection_tree"])}
        self.assertIn(self.collection.pk, collection_pks)
        # other_collection has posts for q but not with theme=T → excluded from sidebar
        self.assertNotIn(self.other_collection.pk, collection_pks)

    def test_keeps_selected_zeroes(self):
        # other_collection is selected but has no pages under theme=T → count 0, still shown
        request = self.search_request(theme=self.theme.slug, collection=self.other_collection.slug)
        site = Site.objects.get(is_default_site=True)
        context = get_facet_context(
            request,
            selection=facet_selection_for(request, site),
            rank_by=RANK_BY_RELEVANCE,
            query=self.search_query,
            enabled_facets={**_all_facets_disabled(), "collection": True, "theme": True},
        )

        collections_by_pk = {taxonomy.pk: taxonomy for taxonomy in _tree_taxonomies(context["collection_tree"])}
        self.assertIn(self.other_collection.pk, collections_by_pk)
        self.assertEqual(collections_by_pk[self.other_collection.pk].result_count, 0)
        current_by_pk = {taxonomy.pk: taxonomy for taxonomy in context["selected_collections"]}
        self.assertEqual(current_by_pk[self.other_collection.pk].result_count, 0)


class FacetedSearchCountRenderingTest(FacetedSearchTestBase):
    """Sidebar labels render as ``Name (N)`` (see also ``FacetLabelTest``)."""

    def test_search_page_shows_exact_result_count_label(self):
        response = self.client.get(self.search_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, "html.parser")
        labels = [
            label.get_text(strip=True) for label in soup.select(".fr-accordions-group .fr-checkbox-group .fr-label")
        ]
        # Only post_with_collection uses self.collection among "Post*" fixtures
        self.assertIn(f"{self.collection.name} (1)", labels)


class FacetedSearchAccordionStateTest(FacetedSearchTestBase):
    """Every filter accordion starts open, and they can all be open at once."""

    def test_accordions_are_independent(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        group = soup.select_one(".fr-accordions-group")
        self.assertIsNotNone(group)
        # Without this, DSFR closes the other accordions when one is opened.
        self.assertEqual(group["data-fr-group"], "false")

    def test_accordions_start_expanded(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        accordions = soup.select(".fr-accordions-group .fr-accordion")
        self.assertGreater(len(accordions), 1)
        for accordion in accordions:
            with self.subTest(accordion=accordion.select_one(".fr-accordion__btn").get_text(strip=True)):
                button = accordion.select_one(".fr-accordion__btn")
                self.assertEqual(button["aria-expanded"], "true")
                # The modifier keeps the panel open before (and without) DSFR's JS.
                panel = accordion.select_one(f"#{button['aria-controls']}")
                self.assertIn("fr-collapse--expanded", panel["class"])


class FacetedSearchTreeCheckboxTest(FacetedSearchTestBase):
    """Parent/child checkboxes: HTML only. Cascade and indeterminate live in facet_tree.js."""

    def _theme_tree_fixtures(self):
        parent = ThemeFactory(locale=self.index.locale, name="Parent theme", slug="parent-theme")
        child_a = ThemeFactory(locale=self.index.locale, name="Child theme A", slug="child-theme-a", parent=parent)
        child_b = ThemeFactory(locale=self.index.locale, name="Child theme B", slug="child-theme-b", parent=parent)
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post with child theme A",
            slug="post-with-child-theme-a",
            themes=[child_a],
        )
        self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post with child theme B",
            slug="post-with-child-theme-b",
            themes=[child_b],
        )
        return parent, child_a, child_b

    def test_tree_checkboxes_have_no_inline_onchange(self):
        parent, child_a, _child_b = self._theme_tree_fixtures()
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        parent_input = soup.select_one(f"#facet-theme-{parent.slug}")
        child_input = soup.select_one(f"#facet-theme-{child_a.slug}")
        self.assertIsNotNone(parent_input)
        self.assertIsNotNone(child_input)
        self.assertFalse(parent_input.has_attr("onchange"))
        self.assertFalse(child_input.has_attr("onchange"))
        tag_input = soup.select_one(f"#facet-tag-{self.tag.slug}")
        self.assertIsNotNone(tag_input)
        self.assertEqual(tag_input.get("onchange"), "this.form.submit()")

    def test_tree_script_is_included(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        self.assertTrue(soup.select_one('script[src*="facet_tree.js"]'))

    def test_all_selected_children_and_parent_render_checked(self):
        parent, child_a, child_b = self._theme_tree_fixtures()
        response = self.client.get(self.search_url(theme=[parent.slug, child_a.slug, child_b.slug]))
        soup = BeautifulSoup(response.content, "html.parser")
        for slug in (parent.slug, child_a.slug, child_b.slug):
            with self.subTest(slug=slug):
                checkbox = soup.select_one(f"#facet-theme-{slug}")
                self.assertIsNotNone(checkbox)
                self.assertTrue(checkbox.has_attr("checked"))

    def test_partial_child_selection_leaves_parent_unchecked(self):
        parent, child_a, child_b = self._theme_tree_fixtures()
        response = self.client.get(self.search_url(theme=child_a.slug))
        soup = BeautifulSoup(response.content, "html.parser")
        parent_input = soup.select_one(f"#facet-theme-{parent.slug}")
        child_a_input = soup.select_one(f"#facet-theme-{child_a.slug}")
        child_b_input = soup.select_one(f"#facet-theme-{child_b.slug}")
        self.assertIsNotNone(parent_input)
        self.assertFalse(parent_input.has_attr("checked"))
        self.assertTrue(child_a_input.has_attr("checked"))
        self.assertFalse(child_b_input.has_attr("checked"))


class FacetedSearchDsfrCheckboxBackportTest(SimpleTestCase):
    """Fail when django-dsfr ships DSFR 1.15+ so the CSS backport can be deleted."""

    def test_upstream_dsfr_does_not_style_indeterminate_checkboxes(self):
        css = Path(dsfr.__file__).resolve().parent / "static/dsfr/dist/component/checkbox/checkbox.min.css"
        self.assertTrue(css.is_file(), f"Missing bundled DSFR checkbox CSS at {css}")
        self.assertNotIn(
            ":indeterminate",
            css.read_text(),
            "django-dsfr now styles :indeterminate checkboxes. "
            "Delete the DSFR 1.15 backport in faceted_search/static/faceted_search/css/faceted_search.css "
            "and this test.",
        )

    def test_backport_sets_background_image_with_dash_svg(self):
        """1.14 only paints `--data-uri-svg` when background-image lists it (see :checked)."""
        css = (Path(__file__).resolve().parents[1] / "static/faceted_search/css/faceted_search.css").read_text()
        start = css.index(":indeterminate")
        end = css.index("end backport")
        block = css[start:end]
        self.assertIn("background-image", block)
        self.assertIn("var(--data-uri-svg)", block)
        self.assertIn("M5 11h14v2H5v-2Z", block)


class FacetedSearchResultsDisplayTest(FacetedSearchTestBase):
    """Test that search result items display metadata (date, themes, collections)."""

    def test_search_results_show_publication_date(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        result_li = soup.find("a", string=self.post_with_collection.title).find_parent("li")
        self.assertIn(self.post_with_collection.date.strftime("%d/%m/%Y"), result_li.get_text())

    def test_search_results_show_collections_and_themes(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")

        collection_li = soup.find("a", string=self.post_with_collection.title).find_parent("li")
        collection_tags = [tag.get_text(strip=True) for tag in collection_li.select(".fr-tag")]
        self.assertIn(self.collection.name, collection_tags)

        theme_li = soup.find("a", string=self.post_with_theme.title).find_parent("li")
        theme_tags = [tag.get_text(strip=True) for tag in theme_li.select(".fr-tag")]
        self.assertIn(self.theme.name, theme_tags)

    def test_search_results_truncate_collections_when_more_than_four(self):
        extra_collections = [CollectionFactory(locale=self.index.locale) for _ in range(4)]
        post = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post with many collections",
            slug="post-with-many-collections",
            collections=[self.collection, self.other_collection] + extra_collections,
        )
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        result_li = soup.find("a", string=post.title).find_parent("li")
        tags = [tag.get_text(strip=True) for tag in result_li.select(".fr-tag")]
        all_collection_names = {self.collection.name, self.other_collection.name} | {
            collection.name for collection in extra_collections
        }
        displayed_collections = [tag for tag in tags if tag in all_collection_names]
        self.assertEqual(len(displayed_collections), 4)
        self.assertIn("+2", tags)

    def test_search_results_truncate_themes_when_more_than_four(self):
        extra_themes = [ThemeFactory(locale=self.index.locale) for _ in range(4)]
        post = self.entry_page_factory(
            parent=self.index,
            owner=self.admin,
            title="Post with many themes",
            slug="post-with-many-themes",
            themes=[self.theme, self.other_theme] + extra_themes,
        )
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        result_li = soup.find("a", string=post.title).find_parent("li")
        tags = [tag.get_text(strip=True) for tag in result_li.select(".fr-tag")]
        all_theme_names = {self.theme.name, self.other_theme.name} | {theme.name for theme in extra_themes}
        displayed_themes = [tag for tag in tags if tag in all_theme_names]
        self.assertEqual(len(displayed_themes), 4)
        self.assertIn("+2", tags)


class FacetCountsWithRankingTest(WagtailPageTestCase):
    """Facet counts follow ``searchable_pages`` (ContentPages drop out for ``rank_by=date``).

    Uses RequestFactory only — no full page render.
    """

    search_query = "Report"

    @classmethod
    def setUpTestData(cls):
        cls.home = Page.objects.get(slug="home")
        cls.admin = get_user_model().objects.create_superuser("rank-counts", "rank@test.test", "pass")
        cls.index = PublicationIndexPageFactory(parent=cls.home, owner=cls.admin)
        cls.tag = TagFactory(name="Report-only tag", slug="report-only-tag")
        cls.theme = ThemeFactory(locale=cls.index.locale, name="Report theme", slug="report-theme")

        content_page = cls.home.add_child(
            instance=ContentPage(
                title="Report content page",
                body=[("paragraph", RichText("<p>Report content for search.</p>"))],
                slug="report-content-for-counts",
                owner=cls.admin,
            )
        )
        content_page.tags.add(cls.tag)
        content_page.save_revision().publish()

        PublicationPageFactory(
            parent=cls.index,
            owner=cls.admin,
            title="Report publication",
            slug="report-publication-for-counts",
            themes=[cls.theme],
        )

    def _counts(self, **params):
        request = RequestFactory().get("/search/", {"q": self.search_query, **params})
        request.user = AnonymousUser()
        site = Site.objects.get(is_default_site=True)
        form = validated_form_for(request, site)
        return compute_facet_result_counts(
            request,
            site,
            self.search_query,
            get_facet_selection_from_form(form),
            rank_by=form.cleaned_data["rank_by"],
            enabled_facets={**dict.fromkeys(ENABLED_FACETS, False), "tag": True, "theme": True},
        )

    def test_date_ranking_excludes_content_pages_from_tag_counts(self):
        relevance = self._counts()
        self.assertEqual(relevance["tag"].get(self.tag.pk, 0), 1)
        self.assertEqual(relevance["theme"].get(self.theme.pk, 0), 1)

        by_date = self._counts(rank_by="date")
        self.assertEqual(by_date["tag"].get(self.tag.pk, 0), 0)
        self.assertEqual(by_date["theme"].get(self.theme.pk, 0), 1)
