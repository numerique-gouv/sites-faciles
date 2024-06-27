import re
from html import unescape
from io import BytesIO

from bs4 import BeautifulSoup
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from wagtail.models import Collection, Site
from wagtailmenus.models.menuitems import MainMenuItem
from wagtailmenus.models.menus import FlatMenu, MainMenu


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


def get_or_create_collection(col_name: str) -> Collection:
    qs = Collection.objects.filter(name=col_name)
    if qs.count():
        return qs.first()
    else:
        root_coll = Collection.get_first_root_node()
        result = root_coll.add_child(name=col_name)
        return result


def get_or_create_footer_menu() -> FlatMenu:
    """
    Get the footer menu or create it if it doesn't already exist

    In any case, return it.
    """

    default_site = Site.objects.filter(is_default_site=True).first()
    footer_menu = FlatMenu.objects.filter(handle="footer", site=default_site).first()

    if not footer_menu:
        footer_menu = FlatMenu.objects.create(title="Pied de page", handle="footer", site=default_site)

    return footer_menu


def get_or_create_main_menu() -> MainMenu:
    """
    Get the main menu or create it if it doesn't already exist

    In any case, return it.
    """

    default_site = Site.objects.filter(is_default_site=True).first()
    main_menu = MainMenu.objects.filter(site=default_site).first()

    if not main_menu:
        main_menu = MainMenu.objects.create(site=default_site, max_levels=2)

        # Init the main menu with the home page
        home_page = default_site.root_page

        menu_item = {
            "sort_order": 0,
            "link_page": home_page,
            "link_text": "Accueil",
            "menu": main_menu,
        }
        MainMenuItem.objects.create(**menu_item)

    return main_menu


def get_streamblock_raw_text(block) -> str:
    """
    Get the raw text of a streamblock.
    """

    # Remove entirely some block types
    removable_blocks = ["image", "alert", "video", "stepper", "separator", "html", "iframe"]

    raw_text = ""
    if block.block.name == "imageandtext":
        raw_text += block.value["text"].source
    elif block.block.name == "multicolumns":
        for column in block.value["columns"]:
            raw_text += get_streamblock_raw_text(column)
    elif block.block.name not in removable_blocks:
        raw_text += block.render()

    return raw_text


def get_streamfield_raw_text(streamfield, max_words: int | None = None) -> str:
    """
    Get the raw text of a streamfield. Used to pre-fill the search description field
    """

    raw_html = ""
    raw_text = ""
    for block in streamfield:
        raw_html += get_streamblock_raw_text(block)

    if not raw_html:
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")
    raw_text += soup.get_text(" ")

    raw_text = unescape(raw_text)
    raw_text = re.sub(r" +", " ", raw_text).strip()

    if max_words:
        words = raw_text.split()
        raw_text = " ".join(words[:max_words]) + " […]"

    return raw_text
