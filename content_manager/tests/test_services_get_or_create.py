from wagtail.test.utils import WagtailPageTestCase
from wagtailmenus.models.menus import FlatMenu

from content_manager.services.get_or_create import get_or_create_footer_menu


class GetOrCreateTestCase(WagtailPageTestCase):
    def test_get_or_create_footer_menu(self):
        assert FlatMenu.objects.count() == 0

        flat_menu = get_or_create_footer_menu()

        assert FlatMenu.objects.count() == 1
        assert flat_menu.handle == "footer"
