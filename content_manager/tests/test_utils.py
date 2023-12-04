from wagtail.images.models import Image
from wagtail.test.utils import WagtailPageTestCase
from wagtailmenus.models.menus import FlatMenu

from content_manager.utils import get_or_create_footer_menu, import_image


class UtilsTestCase(WagtailPageTestCase):
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
