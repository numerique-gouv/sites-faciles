from django.contrib.auth.models import User
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from content_manager.models import ContentPage


class ContentPageTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.user = User.objects.create_superuser("test", "test@test.test", "pass")
        self.user.save()
        self.content_page = home.add_child(
            instance=ContentPage(
                title="Page de contenu",
                slug="content-page",
                owner=self.user,
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
