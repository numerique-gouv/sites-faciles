from wagtail.models import Collection, PageViewRestriction
from wagtail.test.utils import WagtailPageTestCase
from wagtailmenus.models.menus import FlatMenu

from sites_faciles.blog.services.accessors import (
    get_or_create_collection,
    get_or_create_content_page,
    get_or_create_footer_menu,
)
from sites_faciles.blog.utils import import_image


class FooterMenuAccessorTestCase(WagtailPageTestCase):
    def test_get_or_create_footer_menu(self):
        assert FlatMenu.objects.count() == 0

        flat_menu = get_or_create_footer_menu()

        assert FlatMenu.objects.count() == 1
        assert flat_menu.handle == "footer"


class CollectionAccessorTestCase(WagtailPageTestCase):
    def test_get_or_create_collection(self):
        assert Collection.objects.count() == 1

        new_coll = get_or_create_collection("New collection")

        assert Collection.objects.count() == 2
        assert new_coll.name == "New collection"

        duplicate_coll = get_or_create_collection("New collection")

        assert duplicate_coll.pk == new_coll.pk
        assert Collection.objects.count() == 2


class ContentPageAccessorTestCase(WagtailPageTestCase):
    def setUp(self):
        self.sample_body = [("subpageslist", None)]

    def test_get_or_create_content_page_creates_page(self):
        example_page = get_or_create_content_page("example_page", title="Pages d’exemple", body=self.sample_body)

        assert example_page.title == "Pages d’exemple"
        assert example_page.get_parent().slug == "home"

    def test_get_or_create_content_page_doesnt_overwrite_existing_page(self):
        example_page = get_or_create_content_page("new_page", title="New page", body=self.sample_body)

        duplicate_example_page = get_or_create_content_page("new_page", title="Duplicate Page", body=self.sample_body)

        assert example_page.pk == duplicate_example_page.pk
        assert example_page.title == duplicate_example_page.title == "New page"

    def test_get_or_create_content_page_with_parent(self):
        main_page = get_or_create_content_page("main_page", title="Main page", body=self.sample_body)

        sub_page = get_or_create_content_page(
            "sub_page", title="Sub page", body=self.sample_body, parent_page=main_page
        )

        assert sub_page.get_parent().slug == main_page.slug

    def test_get_or_create_private_content_page(self):
        private = get_or_create_content_page(
            "private", title="Private page", body=self.sample_body, restriction_type="login"
        )

        assert PageViewRestriction.objects.filter(page_id=private.pk).first().restriction_type == "login"

    def test_get_or_create_content_page_with_header_fields(self):
        image_file = "static/artwork/technical-error.svg"
        image = import_image(image_file, "Sample image")

        header_fields = {
            "header_image": image,
            "header_color_class": "blue-france",
            "header_with_title": True,
            "header_large": True,
            "header_darken": True,
            "header_cta_text": "Call to action",
        }

        page_with_header = get_or_create_content_page(
            "page_with_header", title="Page with header", body=self.sample_body, page_fields=header_fields
        )

        assert page_with_header.header_image.title == "Sample image"
        assert page_with_header.header_color_class == "blue-france"
        assert page_with_header.header_with_title is True
        assert page_with_header.header_large is True
        assert page_with_header.header_darken is True
        assert page_with_header.header_cta_text == "Call to action"
