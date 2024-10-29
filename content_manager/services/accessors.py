import sys

from django.core.management.color import color_style
from wagtail.models import Collection, PageViewRestriction, Site
from wagtailmenus.models.menuitems import MainMenuItem
from wagtailmenus.models.menus import FlatMenu, MainMenu

from content_manager.constants import HEADER_FIELDS
from content_manager.models import ContentPage

style = color_style()

"""
Methods to get or create various type of contents.
Moved from utils to avoid circular module dependencies.
"""


def get_or_create_collection(col_name: str) -> Collection:
    qs = Collection.objects.filter(name=col_name)
    if qs.count():
        return qs.first()
    else:
        root_coll = Collection.get_first_root_node()
        result = root_coll.add_child(name=col_name)
        return result


def get_or_create_content_page(
    slug: str,
    title: str,
    body: list,
    parent_page: ContentPage | None = None,
    restriction_type: str | None = None,
    page_fields: dict | None = None,
) -> ContentPage:
    """
    Get a ContentPage, or creates it if it exists.
    """

    # If parent_page is not passed as parameter, use the Home page of the default site.
    if not parent_page:
        site = Site.objects.filter(is_default_site=True).first()
        parent_page = site.root_page

    # Don't replace or duplicate an already existing page
    already_exists = ContentPage.objects.filter(slug=slug).first()
    if already_exists:
        sys.stdout.write(f"The {slug} page seem to already exist with id {already_exists.id}\n")
        return already_exists

    new_page = parent_page.add_child(
        instance=ContentPage(
            title=title,
            body=body,
            slug=slug,
            show_in_menus=True,
        )
    )

    allowed_page_fields = HEADER_FIELDS + ["source_url"]
    if page_fields and len(page_fields):
        for k, v in page_fields.items():
            if k in allowed_page_fields:
                setattr(new_page, k, v)
        new_page.save()

    if restriction_type:
        PageViewRestriction.objects.create(page=new_page, restriction_type=restriction_type)

    sys.stdout.write(style.SUCCESS(f"Page {slug} created with id {new_page.id}"))

    return new_page


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
