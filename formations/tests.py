from django.test import TestCase
from django.urls import reverse

from formations.enums import Attendance, Kind
from formations.factories import (
    FormationPageFactory,
    OrganizerFactory,
    SubThemeFactory,
    TargetAudienceFactory,
    ThemeFactory,
)


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

    def test_view_formations_list_sub_theme_filter(self):
        sub_theme1 = SubThemeFactory()
        sub_theme2 = SubThemeFactory()
        sub_theme3 = SubThemeFactory()
        # unused sub theme
        SubThemeFactory()

        formation_with_sub_theme_1and3 = FormationPageFactory(sub_themes=[sub_theme1, sub_theme3])
        formation_with_sub_theme_2 = FormationPageFactory(sub_themes=[sub_theme2])
        formation_without_sub_theme = FormationPageFactory()

        url = reverse("formations_list")

        # no sub theme filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_sub_theme_1and3.name)
        self.assertContains(response, formation_with_sub_theme_2.name)
        self.assertContains(response, formation_without_sub_theme.name)

        # one sub theme filter
        response = self.client.get(url, {"sub_themes": [sub_theme1.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_sub_theme_1and3.name)
        self.assertNotContains(response, formation_with_sub_theme_2.name)
        self.assertNotContains(response, formation_without_sub_theme.name)

        # two sub theme filters
        response = self.client.get(url, {"sub_themes": [sub_theme1.id, sub_theme2.id]})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_sub_theme_1and3.name)
        self.assertContains(response, formation_with_sub_theme_2.name)
        self.assertNotContains(response, formation_without_sub_theme.name)

    def test_view_formations_list_target_audience_filter(self):
        target_audience1 = TargetAudienceFactory()
        target_audience2 = TargetAudienceFactory()
        target_audience3 = TargetAudienceFactory()

        # unused target audience
        TargetAudienceFactory()

        formation_with_target_audience_1and3 = FormationPageFactory(
            target_audience=[target_audience1, target_audience3]
        )
        formation_with_target_audience_2 = FormationPageFactory(target_audience=[target_audience2])
        formation_without_target_audience = FormationPageFactory()

        url = reverse("formations_list")

        # no target audience filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_target_audience_1and3.name)
        self.assertContains(response, formation_with_target_audience_2.name)
        self.assertContains(response, formation_without_target_audience.name)

        # with target audience filter
        response = self.client.get(url, {"target_audience": target_audience1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_target_audience_1and3.name)
        self.assertNotContains(response, formation_with_target_audience_2.name)
        self.assertNotContains(response, formation_without_target_audience.name)

    def test_view_formations_list_organizer_filter(self):
        organizer1 = OrganizerFactory()
        organizer2 = OrganizerFactory()
        organizer3 = OrganizerFactory()
        # unused organizer
        OrganizerFactory()

        formation_with_organizer_1and3 = FormationPageFactory(organizers=[organizer1, organizer3])
        formation_with_organizer_2 = FormationPageFactory(organizers=[organizer2])
        formation_without_organizer = FormationPageFactory()

        url = reverse("formations_list")

        # no organizer filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_organizer_1and3.name)
        self.assertContains(response, formation_with_organizer_2.name)
        self.assertContains(response, formation_without_organizer.name)

        # with organizer filter
        response = self.client.get(url, {"organizer": organizer1.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_organizer_1and3.name)
        self.assertNotContains(response, formation_with_organizer_2.name)
        self.assertNotContains(response, formation_without_organizer.name)

    def test_view_formations_list_kind_filter(self):
        formation_with_kind_formation = FormationPageFactory(kind=Kind.FORMATION)
        formation_with_kind_parcours = FormationPageFactory(kind=Kind.PARCOURS)
        formation_without_kind = FormationPageFactory(kind=Kind.CYCLE)

        url = reverse("formations_list")

        # no kind filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_kind_formation.name)
        self.assertContains(response, formation_with_kind_parcours.name)
        self.assertContains(response, formation_without_kind.name)

        # with kind filter
        response = self.client.get(url, {"kind": Kind.FORMATION})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_kind_formation.name)
        self.assertNotContains(response, formation_with_kind_parcours.name)
        self.assertNotContains(response, formation_without_kind.name)

    def test_view_formations_list_attendance_filter(self):
        formation_with_attendance_online = FormationPageFactory(attendance=Attendance.ENLIGNE)
        formation_with_attendance_presential = FormationPageFactory(attendance=Attendance.PRESENTIEL)
        formation_without_attendance = FormationPageFactory(attendance=Attendance.HYBRIDE)

        url = reverse("formations_list")

        # no attendance filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_attendance_online.name)
        self.assertContains(response, formation_with_attendance_presential.name)
        self.assertContains(response, formation_without_attendance.name)

        # with attendance filter
        response = self.client.get(url, {"attendance": Attendance.ENLIGNE})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_attendance_online.name)
        self.assertNotContains(response, formation_with_attendance_presential.name)
        self.assertNotContains(response, formation_without_attendance.name)

    def test_view_formations_list_search_filter(self):
        # create 3 formations with matching name, short description and knowledge at the end
        formation_with_name_matching = FormationPageFactory(name="Formation matching")
        formation_with_short_description_matching = FormationPageFactory(short_description="Formation matching")
        formation_with_knowledge_at_the_end_matching = FormationPageFactory(knowledge_at_the_end="Formation matching")
        # create other formation with no matching name, short description and knowledge at the end
        formation_without_matching = FormationPageFactory(
            name="Other formation", short_description="Other formation", knowledge_at_the_end="Other formation"
        )

        url = reverse("formations_list")

        # no search filter
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_name_matching.name)
        self.assertContains(response, formation_with_short_description_matching.name)
        self.assertContains(response, formation_with_knowledge_at_the_end_matching.name)
        self.assertContains(response, formation_without_matching.name)

        # with search filter
        response = self.client.get(url, {"search": "matching"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_with_name_matching.name)
        self.assertContains(response, formation_with_short_description_matching.name)
        self.assertContains(response, formation_with_knowledge_at_the_end_matching.name)
        self.assertNotContains(response, formation_without_matching.name)
