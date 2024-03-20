from django.contrib.auth.models import User
from django.core.management import call_command
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from content_manager.models import ContentPage


class ContentPageTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()
        self.content_page = home.add_child(
            instance=ContentPage(
                title="Page de contenu",
                slug="content-page",
                owner=self.admin,
            )
        )
        self.content_page.save()

    def test_content_page_is_renderable(self):
        self.assertPageIsRenderable(self.content_page)

    def test_content_page_has_minimal_content(self):
        url = self.content_page.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "<title>Page de contenu — Titre du site</title>",
        )


class MegaMenuTestCase(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("create_starter_pages")
        call_command("create_demo_pages")

    def test_mega_menu_is_rendered(self):
        self.home_page = ContentPage.objects.get(slug="home")
        self.assertPageIsRenderable(self.home_page)
        response = self.client.get(self.home_page.url)

        self.assertContains(
            response,
            '<p class="fr-hidden fr-displayed-lg">Ceci est une description</p>',
        )
