from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase

from content_manager.models import ContentPage
from content_manager.services.accessors import get_or_create_content_page

User = get_user_model()


class SearchResultsTestCase(WagtailPageTestCase):
    def setUp(self):
        home_page = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")

        # Common body for the two content pages
        body = []

        text_raw = """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"""
        body.append(("paragraph", RichText(text_raw)))

        self.admin.save()
        self.public_content_page = home_page.add_child(
            instance=ContentPage(
                title="Page de contenu publique",
                body=body,
                slug="public-content-page",
                owner=self.admin,
            )
        )
        self.public_content_page.save_revision().publish()

        self.private_content_page = get_or_create_content_page(
            "private-content-page",
            title="Page de contenu privée",
            body=[("subpageslist", None)],
            parent_page=home_page,
            restriction_type="login",
        )
        self.private_content_page.save_revision().publish()

        self.draft_content_page = home_page.add_child(
            instance=ContentPage(
                title="Page de contenu brouillon",
                body=body,
                slug="draft-content-page",
                owner=self.admin,
            )
        )
        self.draft_content_page.save_revision()  # Not published

        call_command("update_index")

    def test_search_public_content_page_is_found(self):

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=Lorem")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Page de contenu publique")

    def test_search_private_content_page_is_not_found(self):

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=Lorem")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Page de contenu privée")

    def test_search_draft_content_page_is_not_found(self):
        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=Lorem")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Page de contenu brouillon")

    def test_search_unpublished_content_page_is_not_found(self):
        self.public_content_page.unpublish()
        call_command("update_index")

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=Lorem")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Page de contenu publique")

    def test_search_no_result(self):
        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=NonExistentTerm")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun résultat trouvé")

    def test_search_no_query(self):
        search_url = reverse("cms_search")
        response = self.client.get(search_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aucun résultat trouvé")

    def test_search_page_on_other_site_is_not_found(self):
        # Create another site with its own root page
        other_home_page = Page.objects.get(slug="home").add_child(
            instance=ContentPage(
                title="Other Site Home",
                slug="other-site-home",
                owner=self.admin,
            )
        )
        other_home_page.save_revision().publish()

        _other_site = Site.objects.create(
            hostname="othersite.test",
            root_page=other_home_page,
            is_default_site=False,
        )

        other_content_page = other_home_page.add_child(
            instance=ContentPage(
                title="Other Site Content Page",
                body=[],
                slug="other-site-content-page",
                owner=self.admin,
            )
        )
        other_content_page.save_revision().publish()

        call_command("update_index")

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=Other")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Other Site Content Page")

    def test_search_page_in_another_language_is_not_found(self):
        # Create an English version of the public content page
        english_page = self.public_content_page.copy(
            to=self.public_content_page.get_parent(),
            lang="en",
            alias=True,
        )
        english_page.title = "Public Content Page in English"
        english_page.slug = "public-content-page-en"
        english_page.save_revision().publish()

        call_command("update_index")

        search_url = reverse("cms_search")
        response = self.client.get(f"{search_url}?q=English")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Public Content Page in English")
