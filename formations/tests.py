from django.core import management
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse

from content_manager.factories import ContentPageFactory
from formations.factories import FormationPageFactory, TargetAudienceFactory, ThemeFactory


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

    def test_view_formations_list_target_audience_filter(self):
        target_audience1 = TargetAudienceFactory()
        target_audience2 = TargetAudienceFactory()
        target_audience3 = TargetAudienceFactory()

        formation_with_target_audience_1and2 = FormationPageFactory(
            target_audience=[target_audience1, target_audience2]
        )
        formation_with_target_audience_2 = FormationPageFactory(target_audience=[target_audience2])
        formation_with_target_audience_3 = FormationPageFactory(target_audience=[target_audience3])
        formation_without_target_audience = FormationPageFactory()

        url = reverse("formations_list")

        # no target audience filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_target_audience_1and2.name)
        self.assertContains(response, formation_with_target_audience_2.name)
        self.assertContains(response, formation_with_target_audience_3.name)
        self.assertContains(response, formation_without_target_audience.name)

        # one theme filter
        response = self.client.get(url, {"target_audience": target_audience2.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_target_audience_1and2.name)
        self.assertContains(response, formation_with_target_audience_2.name)
        self.assertNotContains(response, formation_with_target_audience_3.name)
        self.assertNotContains(response, formation_without_target_audience.name)

    def test_view_formations_list_filters(self):
        theme1 = ThemeFactory()
        theme2 = ThemeFactory()
        target_audience1 = TargetAudienceFactory()
        target_audience2 = TargetAudienceFactory()

        formation_with_wanted_criteria = FormationPageFactory(
            themes=[theme1],
            target_audience=[target_audience1],
        )
        formation_with_other_criteria = FormationPageFactory(
            themes=[theme2],
            target_audience=[target_audience2],
        )
        formation_without_criteria = FormationPageFactory()

        url = reverse("formations_list")

        # no filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_wanted_criteria.name)
        self.assertContains(response, formation_with_other_criteria.name)
        self.assertContains(response, formation_without_criteria.name)

        # target audience and theme filter
        response = self.client.get(url, {"themes": [theme1.id], "target_audience": target_audience1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_wanted_criteria.name)
        self.assertNotContains(response, formation_with_other_criteria.name)
        self.assertNotContains(response, formation_without_criteria.name)
