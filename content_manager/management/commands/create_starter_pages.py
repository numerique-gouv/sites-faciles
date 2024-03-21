from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.rich_text import RichText
from wagtailmenus.models.menuitems import FlatMenuItem

from content_manager.models import ContentPage
from content_manager.utils import get_or_create_footer_menu, import_image


ALL_ALLOWED_SLUGS = ["home", "mentions-legales", "accessibilite"]


class Command(BaseCommand):
    help = """
    Creates a series of starter pages, in order to avoid new sites having only a
    blank "Welcome to Wagtail" page.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--slug", nargs="+", type=str, help="[Optional] Slug of the page(s) to create", choices=ALL_ALLOWED_SLUGS
        )

    def handle(self, *args, **kwargs):
        slugs = kwargs.get("slug")

        if not slugs:
            slugs = ALL_ALLOWED_SLUGS

        for slug in slugs:
            if slug == "home":
                self.create_homepage()
            elif slug == "mentions-legales":
                title = "Mentions légales"
                body = []

                alert_block = {
                    "title": title,
                    "description": """Entrez ici les mentions légales du site.<br />
                    <a href="https://www.francenum.gouv.fr/guides-et-conseils/developpement-commercial/site-web/quelles-sont-les-mentions-legales-pour-un-site">
                    Que doivent-elles obligatoirement contenir ?</a>""",  # noqa
                    "level": "info",
                    "heading_tag": "h2",
                }
                body.append(("alert", alert_block))

                text_raw = """
                <p>D’après la <a href="https://www.systeme-de-design.gouv.fr/elements-d-interface/composants/pied-de-page">documentation du système de design</a>,
                le pied de page doit contenir a minima les quatre liens suivants :</p>
                <ul>
                    <li>Accessibilité : non/partiellement/totalement conforme</li>
                    <li>Mentions légales</li>
                    <li>Données personnelles</li>
                    <li>Gestion des cookies</li>
                </ul>
                <p>Ces deux derniers peuvent pointer vers des pages à part entière ou des sections de cette page.</p>
                """  # noqa
                body.append(("paragraph", RichText(text_raw)))

                self.create_page(slug=slug, title=title, body=body)
            elif slug == "accessibilite":
                title = "Déclaration d’accessibilité"
                body = []

                alert_block = {
                    "title": title,
                    "description": """Entrez ici la déclaration d’accessibilité.<br />
                    <a href="https://betagouv.github.io/a11y-generateur-declaration/#create">
                    Générateur de déclaration d’accessibilité</a>""",
                    "level": "info",
                    "heading_tag": "h2",
                }

                body.append(("alert", alert_block))
                self.create_page(slug=slug, title=title, body=body, footer_label="Accessibilité : non conforme")
            else:
                raise ValueError(f"Valeur inconnue : {slug}")

    def create_homepage(self) -> None:
        """
        Create the homepage, set it as default and delete the initial page
        """
        # Don't replace a manually created home
        already_exists = ContentPage.objects.filter(slug="home").first()
        if already_exists:
            self.stdout.write(f"The home page seem to already exist with id {already_exists.id}")
            return

        # Create the page
        body = []
        title = "Votre nouveau site avec Sites faciles"

        image = import_image(
            full_path="static/artwork/coding.svg",
            title="Pictogrammes DSFR — Internet",
        )

        text_raw = """<p>Bienvenue !</p>

        <p>Vous venez de créer un site utilisant le gestionnaire de contenus de l’État.</p>

        <p>Vous pouvez maintenant vous connecter dans l’administration et personnaliser le site.</p>
        """

        admin_url = f"{settings.WAGTAILADMIN_BASE_URL}{reverse('wagtailadmin_home')}"

        image_and_text_block = {
            "image": image,
            "image_ratio": "3",
            "text": RichText(text_raw),
            "link_url": admin_url,
            "link_label": "Gérer le site",
        }

        body.append(("imageandtext", image_and_text_block))

        text_2_raw = """
        <p>En particulier, vous devrez :</p>
        <ul>
            <li>Configurer le site dans Configuration > Configuration du site</li>
            <li>Remplacer le contenu de la page de mentions légales</li>
            <li>Remplacer le contenu de cette page d’accueil.</li>
        </ul>
        """
        body.append(("paragraph", RichText(text_2_raw)))

        root = Page.objects.get(slug="root")
        home_page = root.add_child(instance=ContentPage(title=title, body=body, show_in_menus=True))

        # Define it as default for the default site
        site = Site.objects.filter(is_default_site=True).first()

        site.root_page_id = home_page.id
        site.save()

        # Delete the original default page and get its slug
        original_home = Page.objects.get(slug="home")
        original_home.delete()

        home_page.slug = "home"
        home_page.save()

        self.stdout.write(self.style.SUCCESS(f"Homepage created with id {home_page.id}"))

    def create_page(self, slug: str, title: str, body: list, footer_label: str = ""):
        """
        Creates a page for the site and adds it to the footer
        """

        # Don't replace a manually created page
        already_exists = ContentPage.objects.filter(slug=slug).first()
        if already_exists:
            self.stdout.write(f"The {slug} page seem to already exist with id {already_exists.id}")
            return

        home_page = Site.objects.filter(is_default_site=True).first().root_page
        new_page = home_page.add_child(instance=ContentPage(title=title, body=body, slug=slug, show_in_menus=True))

        footer_menu = get_or_create_footer_menu()

        footer_item = {
            "menu": footer_menu,
            "link_page": new_page,
        }
        if footer_label:
            footer_item["link_text"] = footer_label

        FlatMenuItem.objects.create(**footer_item)

        self.stdout.write(self.style.SUCCESS(f"Page {slug} created with id {new_page.id}"))
