from django.core.management.base import BaseCommand
from faker import Faker
from taggit.models import slugify
from wagtail.models import Site
from wagtail.rich_text import RichText
from wagtailmenus.models.menuitems import FlatMenuItem, MainMenuItem
from wagtailmenus.models.menus import FlatMenu, MainMenu

from blog.models import BlogIndexPage
from content_manager.models import ContentPage, MegaMenu, MegaMenuCategory

ALL_ALLOWED_SLUGS = ["blog_index", "publications"]

fake = Faker("fr_FR")


class Command(BaseCommand):
    help = """
    Creates a series of demo pages with a variety of content.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug", nargs="+", type=str, help="[Optional] Slug of the page(s) to create", choices=ALL_ALLOWED_SLUGS
        )

    def handle(self, *args, **kwargs):
        slugs = kwargs.get("slug")

        if not slugs:
            slugs = ALL_ALLOWED_SLUGS

        site = Site.objects.filter(is_default_site=True).first()

        # First, add the home page to the main menu if not already done
        home_page = site.root_page
        main_menu = MainMenu.objects.first()
        if not main_menu:
            main_menu = MainMenu.objects.create(site=site)
        MainMenuItem.objects.update_or_create(
            link_page=home_page, menu=main_menu, defaults={"link_text": "Accueil", "sort_order": 0}
        )

        for slug in slugs:
            if slug == "blog_index":
                blog_index = self.create_blog_index(home_page)
                MainMenuItem.objects.update_or_create(link_page=blog_index, menu=main_menu, defaults={"sort_order": 1})

                # to/do add example blog pages

            elif slug == "publications":
                self.create_publication_pages(site, home_page, main_menu)

            else:
                raise ValueError(f"Valeur inconnue : {slug}")

    def create_blog_index(self, home_page) -> BlogIndexPage:
        """
        Create the blog index
        """

        # Don't replace a manually created page
        already_exists = BlogIndexPage.objects.filter(slug="actualités").first()
        if already_exists:
            self.stdout.write(f"The page seem to already exist with id {already_exists.id}")
            return already_exists

        # Create the page
        body = []
        title = "Actualités"

        text_raw = """<p>Bienvenue !</p>

        <p>Vous trouverez ici nos dernières actualités</p>
        """

        body.append(("paragraph", RichText(text_raw)))

        blog_index = home_page.add_child(
            instance=BlogIndexPage(title=title, body=body, slug="actualités", show_in_menus=True)
        )

        self.stdout.write(self.style.SUCCESS(f"Blog index page created with id {blog_index.id}"))

        return blog_index

    def create_content_page(self, slug: str, title: str, body: list, parent_page: ContentPage) -> ContentPage:
        """
        Creates a page for the site.
        """

        # Don't replace or duplicate an already existing page
        already_exists = ContentPage.objects.filter(slug=slug).first()
        if already_exists:
            self.stdout.write(f"The {slug} page seem to already exist with id {already_exists.id}")
            return already_exists

        new_page = parent_page.add_child(instance=ContentPage(title=title, body=body, slug=slug, show_in_menus=True))

        self.stdout.write(self.style.SUCCESS(f"Page {slug} created with id {new_page.id}"))

        return new_page

    def create_publication_pages(self, site, home_page, main_menu):
        slug = "publications"
        title = "Publications"
        body = []

        text_raw = """<p>Veuillez trouver ici une liste de publications</p>"""
        body.append(("paragraph", RichText(text_raw)))

        publications_page = self.create_content_page(slug=slug, title=title, body=body, parent_page=home_page)
        publications_menu_item, _created = MainMenuItem.objects.update_or_create(
            link_page=publications_page, menu=main_menu, defaults={"sort_order": 2}
        )

        # Create the mega menu
        publications_mega_menu, _created = MegaMenu.objects.get_or_create(
            name="Méga-menu publications",
            parent_menu_item_id=publications_menu_item.id,
            description="Ceci est une description",
        )

        # Create a set of publications sub-pages
        for i in range(4):
            menu_category_menu, _created = FlatMenu.objects.get_or_create(
                site_id=site.id,
                title=f"Menu publications > Catégorie {i + 1}",
                handle=f"mega_menu_section_{i + 1}",
                heading=f"Colonne {i + 1}",
            )

            menu_category, _created = MegaMenuCategory.objects.get_or_create(
                mega_menu=publications_mega_menu, sort_order=i, category=menu_category_menu
            )

            for j in range(8):
                title = f"Page {i + 1} - {j + 1}"

                body = []
                text = ""
                for p in fake.paragraphs():
                    text += f"<p>{p}</p>\n"
                    body.append(("paragraph", RichText(text)))

                new_page = self.create_content_page(
                    slug=slugify(title), title=title, body=body, parent_page=publications_page
                )

                FlatMenuItem.objects.get_or_create(link_page=new_page, menu=menu_category_menu, sort_order=j)

            publications_mega_menu.categories.add(menu_category)
            publications_mega_menu.save()
