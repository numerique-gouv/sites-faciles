from django.core.management import call_command
from django.urls import reverse
from wagtail.test.utils import WagtailPageTestCase

from forms.models import FormPage


class FormsTestCase(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("collectstatic", interactive=False)
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

        self.assertRegex(
            response.content.decode(),
            r"<li class=\"fr-error-text\">(\\n)?\s*(Ce champ est requis|Ce champ est obligatoire)\.(\\n)?\s*<\/li>",
        )
        # Updates sometimes mess with the order of the translations and so the displayed translation. Both are fine.

    def test_form_page_is_found_in_search_results(self):
        call_command("update_index")

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=contact")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML("""<a href="/contact/">Contact</a>""", response.content.decode())
        self.assertInHTML("""<h1>1 résultat pour la recherche «\xa0contact\xa0»</h1>""", response.content.decode())
