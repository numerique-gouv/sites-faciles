from io import BytesIO

from django.core.files.images import ImageFile
from wagtail.images.models import Image
from wagtail.models import Site
from wagtailmenus.models.menus import FlatMenu


def import_image(full_path: str, title: str) -> Image:
    """
    Import an image to the Wagtail medias based on its full path and return it.
    """
    with open(full_path, "rb") as image_file:
        image = Image(
            file=ImageFile(BytesIO(image_file.read()), name=title),
            title=title,
        )
        image.save()
        return image


def get_or_create_footer_menu() -> FlatMenu:
    """
    Get the footer menu or create it if it doesn't already exist

    In any case, return it.
    """

    footer_menu = FlatMenu.objects.filter(handle="footer").first()

    if not footer_menu:
        default_site = Site.objects.filter(is_default_site=True).first()
        footer_menu = FlatMenu.objects.create(title="Pied de page", handle="footer", site=default_site)

    return footer_menu
