from wagtail.images import get_image_model
from wagtail.test.utils import WagtailPageTestCase

from content_manager.utils import import_image

Image = get_image_model()


class UtilsTestCase(WagtailPageTestCase):
    def test_import_image(self):
        image_file = "static/artwork/technical-error.svg"
        image = import_image(image_file, "Sample image")

        assert isinstance(image, Image)
        assert image.title == "Sample image"
