from django.core.management import call_command
from wagtail.test.utils import WagtailPageTestCase

from sites_faciles.forms.models import FormPage


class FormsTestCase(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("collectstatic", "--ignore=*.sass", interactive=False)
        call_command("create_starter_pages")

    def test_form_page_is_renderable(self):
        form_page = FormPage.objects.first()
        self.assertPageIsRenderable(form_page)

    def test_correct_form_is_submitted(self):
        form_page = FormPage.objects.first()
        post_data = {
            "votre_nom_complet": "Félix Faure",
            "votre_adresse_electronique": "no7@elysee.fr",
            "titre_de_votre_message": "Ma connaissance",
            "votre_message": "S’est enfuie par l’escalier !",
        }
        response = self.client.post(form_page.url, post_data)

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "<p>Merci pour votre message ! Nous reviendrons vers vous rapidement.</p>",
        )

    def test_incorrect_form_is_rejected(self):
        form_page = FormPage.objects.first()
        post_data = {
            "votre_nom_complet": "Félix Faure",
            "votre_adresse_electronique": "bad_email",
            "titre_de_votre_message": "",
            "votre_message": "S’est enfuie par l’escalier !",
        }
        response = self.client.post(form_page.url, post_data)

        self.assertEqual(response.status_code, 200)

        self.assertInHTML(
            """<li class="fr-error-text">Saisissez une adresse e-mail valide.</li>""",
            response.content.decode(),
        )

        self.assertInHTML(
            """<li class="fr-error-text">Ce champ est obligatoire.</li>""",
            response.content.decode(),
        )
