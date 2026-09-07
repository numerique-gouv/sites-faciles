"""Tests for the faceted search results view."""

import zoneinfo
from datetime import datetime
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import QueryDict
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase

from faceted_search.forms import FacetedSearchForm
from faceted_search.search import RANK_BY_DATE, RANK_BY_RELEVANCE
from faceted_search.tests.test_facets import FacetedSearchTestBase, get_post_titles_in_response
from faceted_search.views import FacetedSearchResultsView
from publications.tests.factories import PublicationIndexPageFactory, PublicationPageFactory
from sites_conformes.core.models import ContentPage
from sites_conformes.core.tests.test_search import SearchResultsTestCase

PARIS_TZ = zoneinfo.ZoneInfo("Europe/Paris")


class FacetedSearchResultsTestCase(SearchResultsTestCase):
    """Run the core search scenarios against the faceted search view.

    With facets disabled, FacetedSearchResultsView should behave the same as
    the core SearchResultsView.
    """


class FacetedSearchResultsViewTest(FacetedSearchTestBase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()

    def _build_view(self, query=None, user=None):
        request = self.factory.get("/search/", {"q": query} if query else {})
        request.user = user or AnonymousUser()
        request.site = Site.objects.get(is_default_site=True)
        view = FacetedSearchResultsView()
        view.request = request
        view.kwargs = {}
        return view

    def test_get_context_data_includes_facet_context(self):
        view = self._build_view(query=self.search_query)
        view.object_list = view.get_queryset()
        context = view.get_context_data()
        self.assertIn("enabled_facets", context)
        self.assertTrue(context["enabled_facets"]["collection"])
        self.assertIn("collection_tree", context)


class FacetedSearchPaginationTestBase(WagtailPageTestCase):
    """Minimal base for pagination tests: no taxonomy fixtures, just an index and posts."""

    search_query = "Post"

    @classmethod
    def setUpTestData(cls):
        cls.home = Page.objects.get(slug="home")
        cls.admin = get_user_model().objects.create_superuser("test", "test@test.test", "pass")
        cls.index = PublicationIndexPageFactory(parent=cls.home, owner=cls.admin)

    def search_url(self, query=None, **params):
        query = self.search_query if query is None else query
        return f"{reverse('cms_search')}?{urlencode({'q': query, **params}, doseq=True)}"


class FacetedSearchPaginationTest(FacetedSearchPaginationTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        for _ in range(15):
            PublicationPageFactory(parent=cls.index, owner=cls.admin)

    def test_pagination_first_page_is_limited_to_page_size(self):
        response = self.client.get(self.search_url())
        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]
        self.assertEqual(page_obj.paginator.per_page, 10)
        self.assertEqual(page_obj.paginator.count, 15)
        self.assertEqual(len(page_obj), 10)
        self.assertTrue(page_obj.has_next())

        soup = BeautifulSoup(response.content, "html.parser")
        result_items = soup.select("#search-results ol > li")
        self.assertEqual(len(result_items), 10)

    def test_pagination_second_page_shows_remaining_results(self):
        response = self.client.get(self.search_url(page=2))
        self.assertEqual(response.status_code, 200)
        page_obj = response.context["page_obj"]
        self.assertEqual(page_obj.number, 2)
        self.assertEqual(page_obj.paginator.count, 15)
        self.assertEqual(len(page_obj), 5)
        self.assertFalse(page_obj.has_next())

        soup = BeautifulSoup(response.content, "html.parser")
        result_items = soup.select("#search-results ol > li")
        self.assertEqual(len(result_items), 5)

    def test_pagination_widget_appears_when_multiple_pages(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        pagination_nav = soup.select_one("nav.fr-pagination")
        self.assertIsNotNone(pagination_nav)

    def test_pagination_result_count_and_page_size_are_displayed(self):
        response = self.client.get(self.search_url())
        soup = BeautifulSoup(response.content, "html.parser")
        paragraph = soup.select_one("#search-results h2")
        self.assertIsNotNone(paragraph)
        text = paragraph.get_text()
        self.assertIn("15 résultats", text)
        self.assertIn("10 par page", text)

    def test_pagination_result_numbering_continues_across_pages(self):
        response = self.client.get(self.search_url(page=2))
        soup = BeautifulSoup(response.content, "html.parser")
        ol = soup.select_one("#search-results ol")
        self.assertIsNotNone(ol)
        self.assertEqual(int(ol["start"]), 11)
        # DSFR fix : "start" is broken, so we reimplement counters.
        self.assertIn("--list-start: 11", ol["style"])


class AccentInsensitiveSearchTest(FacetedSearchPaginationTestBase):
    """``blé`` and ``ble`` should return the same FTS hits under french_unaccent."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.wheat_page = PublicationPageFactory(
            parent=cls.index,
            owner=cls.admin,
            title="Culture du blé tendre",
            slug="culture-du-ble-tendre",
        )
        cls.other_page = PublicationPageFactory(
            parent=cls.index,
            owner=cls.admin,
            title="Rapport annuel",
            slug="rapport-annuel-unaccent",
        )

    def test_unaccented_query_matches_accented_title(self):
        response = self.client.get(self.search_url(query="ble"))
        titles = get_post_titles_in_response(response)
        self.assertIn(self.wheat_page.title, titles)
        self.assertNotIn(self.other_page.title, titles)

    def test_accented_and_unaccented_queries_return_the_same_results(self):
        accented = get_post_titles_in_response(self.client.get(self.search_url(query="blé")))
        unaccented = get_post_titles_in_response(self.client.get(self.search_url(query="ble")))
        self.assertEqual(accented, unaccented)
        self.assertIn(self.wheat_page.title, accented)


class RankByParamTest(SimpleTestCase):
    """No DB: the form is the only source of the ``rank_by`` value."""

    def test_rank_by_value_and_default(self):
        for query_string, expected in (
            ("", RANK_BY_RELEVANCE),  # default is relevance
            ("rank_by=relevance", RANK_BY_RELEVANCE),
            ("rank_by=date", RANK_BY_DATE),
            ("rank_by=popularity", RANK_BY_RELEVANCE),  # invalid values default to relevance
        ):
            with self.subTest(query_string=query_string):
                form = FacetedSearchForm(QueryDict(query_string))
                self.assertTrue(form.is_valid())
                self.assertEqual(form.cleaned_data["rank_by"], expected)
                # The checked radio must agree with the value the view ranks by.
                self.assertEqual(form["rank_by"].value(), expected)

    def test_rank_by_default_without_data(self):
        self.assertEqual(FacetedSearchForm()["rank_by"].value(), RANK_BY_RELEVANCE)

    def test_form_binds_query_and_ranking_and_ignores_page(self):
        form = FacetedSearchForm(QueryDict("q=Report&page=2&rank_by=date"))
        self.assertEqual(form["q"].value(), "Report")
        self.assertEqual(form["rank_by"].value(), RANK_BY_DATE)
        # page is not a form field, so submitting the form resets pagination.
        self.assertNotIn("page", form.fields)

    def test_form_drops_invalid_years(self):
        form = FacetedSearchForm(QueryDict("q=Report&year=2024&year=nope"))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["year"], ["2024"])


class FacetedSearchRankingTest(FacetedSearchPaginationTestBase):
    """Queryset ranking only (no full page render, to keep runtime down)."""

    search_query = "Report"

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        body = [("paragraph", RichText("<p>Report content for search.</p>"))]
        cls.content_page = cls.home.add_child(
            instance=ContentPage(
                title="Report content page",
                body=body,
                slug="report-content-page",
                owner=cls.admin,
            )
        )
        cls.content_page.save_revision().publish()

        cls.older = PublicationPageFactory(
            parent=cls.index,
            owner=cls.admin,
            title="Older Report",
            slug="older-report",
            date=datetime(2020, 1, 1, 12, 0, 0, tzinfo=PARIS_TZ),
        )
        cls.newer = PublicationPageFactory(
            parent=cls.index,
            owner=cls.admin,
            title="Newer Report",
            slug="newer-report",
            date=datetime(2024, 6, 1, 12, 0, 0, tzinfo=PARIS_TZ),
        )

    def _result_titles(self, **params):
        request = RequestFactory().get("/search/", {"q": self.search_query, **params})
        request.user = AnonymousUser()
        view = FacetedSearchResultsView()
        view.request = request
        view.kwargs = {}
        return [page.title for page in view.get_queryset()]

    def test_rank_by_date_excludes_content_pages_and_orders_by_date(self):
        self.assertIn(self.content_page.title, self._result_titles())
        self.assertIn(self.content_page.title, self._result_titles(rank_by="relevance"))
        self.assertEqual(self._result_titles(rank_by="date"), [self.newer.title, self.older.title])
