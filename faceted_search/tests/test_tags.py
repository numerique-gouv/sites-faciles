from django.test import SimpleTestCase

from faceted_search.templatetags.faceted_search_tags import facet_label, facet_value


class FacetLabelTest(SimpleTestCase):
    """``facet_label`` formats ``Name (N)`` (with ``FacetedSearchCountRenderingTest``)."""

    def test_facet_label_includes_count_when_present(self):
        self.assertEqual(facet_label("Agriculture", 3), "Agriculture (3)")

    def test_facet_label_omits_count_when_missing(self):
        self.assertEqual(facet_label("Agriculture"), "Agriculture")
        self.assertEqual(facet_label("Agriculture", None), "Agriculture")
        self.assertEqual(facet_label("Agriculture", ""), "Agriculture")


class FacetValueTest(SimpleTestCase):
    def setUp(self):
        self.item = type("Item", (), {"pk": 42, "slug": "agriculture"})()

    def test_facet_value_is_the_slug(self):
        self.assertEqual(facet_value(self.item, "theme"), "agriculture")

    def test_facet_value_is_the_pk_for_authors(self):
        self.assertEqual(facet_value(self.item, "author"), 42)
