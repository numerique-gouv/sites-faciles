from django.test import TestCase
from django.urls import reverse

from formations.factories import FormationPageFactory, ThemeFactory


class FormationsTest(TestCase):
    def test_view_formations_list_live_page(self):
        formation_published = FormationPageFactory()
        formation_unpublished = FormationPageFactory(live=False)

        response = self.client.get(reverse("formations_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_published.name)
        self.assertNotContains(response, formation_unpublished.name)

    def test_view_formations_list_theme_filter(self):
        theme1 = ThemeFactory()
        theme2 = ThemeFactory()
        theme3 = ThemeFactory()
        unused_theme = ThemeFactory()

        formation_with_theme_1and3 = FormationPageFactory(themes=[theme1, theme3])
        formation_with_theme_2 = FormationPageFactory(themes=[theme2])
        formation_without_theme = FormationPageFactory()

        url = reverse("formations_list")

        # no theme filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, theme1)
        self.assertContains(response, theme2)
        self.assertContains(response, theme3)
        self.assertNotContains(response, unused_theme)
        self.assertContains(response, formation_with_theme_1and3.name)
        self.assertContains(response, formation_with_theme_2.name)
        self.assertContains(response, formation_without_theme.name)

        # one theme filter
        response = self.client.get(url, {"themes": [theme1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_theme_1and3.name)
        self.assertNotContains(response, formation_with_theme_2.name)
        self.assertNotContains(response, formation_without_theme.name)

        # two theme filters
        response = self.client.get(url, {"themes": [theme1.id, theme2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_theme_1and3.name)
        self.assertContains(response, formation_with_theme_2.name)
        self.assertNotContains(response, formation_without_theme.name)
