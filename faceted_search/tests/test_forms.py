"""Tests for ``FacetedSearchForm``, the single GET form of the search results page.

No DB access: these bind the form directly to a ``QueryDict`` instead of going
through the view. Facet fields are covered in ``test_facets`` since they need
taxonomy fixtures.
"""

from django.http import QueryDict
from django.test import SimpleTestCase

from faceted_search.forms import FacetedSearchForm
from faceted_search.search import RANK_BY_DATE, RANK_BY_RELEVANCE


class RankByFieldTest(SimpleTestCase):
    """The form is the only source of the ``rank_by`` value."""

    def test_falls_back_to_relevance(self):
        for query_string, expected in (
            ("", RANK_BY_RELEVANCE),
            ("rank_by=relevance", RANK_BY_RELEVANCE),
            ("rank_by=date", RANK_BY_DATE),
            ("rank_by=popularity", RANK_BY_RELEVANCE),
        ):
            with self.subTest(query_string=query_string):
                form = FacetedSearchForm(QueryDict(query_string))
                self.assertTrue(form.is_valid())
                self.assertEqual(form.cleaned_data["rank_by"], expected)
                # The checked radio must agree with the value the view ranks by.
                self.assertEqual(form["rank_by"].value(), expected)


class QueryFieldTest(SimpleTestCase):
    def test_binds_query(self):
        form = FacetedSearchForm(QueryDict("q=Report&rank_by=date"))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["q"], "Report")

    def test_accepts_an_empty_query(self):
        form = FacetedSearchForm(QueryDict(""))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["q"], "")


class YearFieldTest(SimpleTestCase):
    """``year`` has no sidebar UI: it round-trips through hidden inputs."""

    def test_drops_invalid_years(self):
        form = FacetedSearchForm(QueryDict("q=Report&year=2024&year=nope"))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["year"], ["2024"])

    def test_renders_selected_years_as_hidden_inputs(self):
        form = FacetedSearchForm(QueryDict("q=Report&year=2024"))
        self.assertInHTML('<input type="hidden" name="year" value="2024" id="id_year_0">', str(form["year"]))
