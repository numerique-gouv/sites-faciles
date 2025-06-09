import csv
from io import StringIO

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
        formation_published = FormationPageFactory(name="Formation published")
        formation_unpublished = FormationPageFactory(name="Formation unpublished", live=False)

        response = self.client.get(reverse("formations_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, formation_published.name)
        self.assertNotContains(response, formation_unpublished.name)

    def test_view_formations_list_theme_filter(self):
        theme1 = ThemeFactory(name="Theme 1")
        theme2 = ThemeFactory(name="Theme 2")
        theme3 = ThemeFactory(name="Theme 3")
        unused_theme = ThemeFactory(name="Unused theme")

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
        sub_theme1 = SubThemeFactory(name="Sub theme 1")
        sub_theme2 = SubThemeFactory(name="Sub theme 2")
        sub_theme3 = SubThemeFactory(name="Sub theme 3")
        # unused sub theme
        SubThemeFactory(name="Unused sub theme")

        formation_with_sub_theme_1and3 = FormationPageFactory(
            name="Formation with sub theme 1 and 3", sub_themes=[sub_theme1, sub_theme3]
        )
        formation_with_sub_theme_2 = FormationPageFactory(name="Formation with sub theme 2", sub_themes=[sub_theme2])
        formation_without_sub_theme = FormationPageFactory(name="Formation without sub theme")

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
        target_audience1 = TargetAudienceFactory(name="Target audience 1")
        target_audience2 = TargetAudienceFactory(name="Target audience 2")
        target_audience3 = TargetAudienceFactory(name="Target audience 3")

        # unused target audience
        TargetAudienceFactory(name="Unused target audience")

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
        organizer1 = OrganizerFactory(name="Organizer 1")
        organizer2 = OrganizerFactory(name="Organizer 2")
        organizer3 = OrganizerFactory(name="Organizer 3")
        # unused organizer
        OrganizerFactory(name="Unused organizer")

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
        formation_with_kind_formation = FormationPageFactory(name="Formation with kind formation", kind=Kind.FORMATION)
        formation_with_kind_parcours = FormationPageFactory(name="Formation with kind parcours", kind=Kind.PARCOURS)
        formation_without_kind = FormationPageFactory(name="Formation without kind", kind=Kind.CYCLE)

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
        formation_with_attendance_online = FormationPageFactory(
            name="Formation with attendance online", attendance=Attendance.ENLIGNE
        )
        formation_with_attendance_presential = FormationPageFactory(
            name="Formation with attendance presential", attendance=Attendance.PRESENTIEL
        )
        formation_without_attendance = FormationPageFactory(
            name="Formation without attendance", attendance=Attendance.HYBRIDE
        )

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

    def test_export_csv(self):
        # Create test data
        theme = ThemeFactory(name="Test Theme")
        sub_theme = SubThemeFactory(name="Test Sub Theme")
        target_audience = TargetAudienceFactory(name="Test Audience")
        organizer = OrganizerFactory(name="Test Organizer")

        formation = FormationPageFactory(
            name="Test Formation",
            kind=Kind.FORMATION,
            short_description="Test Description",
            knowledge_at_the_end="Test Objectives",
            duration="2h",
            registration_link="https://campus.numerique.gouv.fr/",
            themes=[theme],
            sub_themes=[sub_theme],
            target_audience=[target_audience],
            organizers=[organizer],
            attendance=Attendance.ENLIGNE,
        )

        # Test CSV export
        response = self.client.get(reverse("formations_list"), {"export": "csv"})

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="formations.csv"')

        # Parse CSV content
        csv_content = StringIO(response.content.decode("utf-8"))
        reader = csv.reader(csv_content)

        # Check headers
        headers = next(reader)
        expected_headers = [
            "Intitulé",
            "Type",
            "Descriptif court",
            "Objectifs",
            "Durée",
            "Lien d'inscription",
            "Public cible",
            "Thématiques",
            "Sous-thématiques",
            "Organisateurs",
            "Modalité",
        ]
        self.assertEqual(headers, expected_headers)

        # Check data
        row = next(reader)
        self.assertEqual(row[0], formation.name)
        self.assertEqual(row[1], formation.get_kind_display())
        self.assertEqual(row[2], formation.short_description)
        self.assertEqual(row[3], formation.knowledge_at_the_end)
        self.assertEqual(row[4], formation.duration)
        self.assertEqual(row[5], formation.registration_link)
        self.assertEqual(row[6], str(target_audience))
        self.assertEqual(row[7], str(theme))
        self.assertEqual(row[8], str(sub_theme))
        self.assertEqual(row[9], str(organizer))
        self.assertEqual(row[10], formation.get_attendance_display())

    def test_export_csv_with_filters(self):
        # Create test data
        theme1 = ThemeFactory(name="Theme 1")
        theme2 = ThemeFactory(name="Theme 2")

        formation1 = FormationPageFactory(name="Formation 1", themes=[theme1])
        # formation2 has theme2 but is not appearing in the export because of the theme filter
        FormationPageFactory(name="Formation 2", themes=[theme2])

        # Test CSV export with theme filter
        response = self.client.get(reverse("formations_list"), {"export": "csv", "themes": [theme1.id]})

        # Parse CSV content
        csv_content = StringIO(response.content.decode("utf-8"))
        reader = csv.reader(csv_content)

        # Skip headers
        next(reader)

        # Check that only formation1 is in the export
        rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], formation1.name)
