from django.contrib.auth.models import User
from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase
from wagtailmenus.models.menus import FlatMenu

from content_manager.models import ContentPage
from content_manager.utils import get_or_create_footer_menu, import_image


class UtilsTestCase(WagtailPageTestCase):
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

    def test_import_image(self):
        image_file = "static/artwork/technical-error.svg"
        image = import_image(image_file, "Sample image")

        assert isinstance(image, Image)
        assert image.title == "Sample image"

    def test_get_or_create_footer_menu(self):
        assert FlatMenu.objects.count() == 0

        flat_menu = get_or_create_footer_menu()

        assert FlatMenu.objects.count() == 1
        assert flat_menu.handle == "footer"
