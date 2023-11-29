from django.core.management.base import BaseCommand
from django.urls import reverse
from wagtail.models import Page, Site
from wagtail.rich_text import RichText

from content_manager.models import ContentPage


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--slug", nargs="+", type=str, help="[Optional] Slug of the page(s) to create")

    def handle(self, *args, **kwargs):
        slugs = kwargs.get("slug")

        if not slugs:
            slugs = ["home"]

        for slug in slugs:
            self.create_page(slug)

    def create_page(self, slug: str):
        if slug == "home":
            self.create_page_home()
        else:
            raise ValueError(f"Valeur inconnue : {slug}")

    def create_page_home(self):
        """
        Create the home page, set it as default and delete the sample page
        """

        # Create the page
        title = "Votre nouveau site avec le CMS beta"
        body = []

        body.append(("title", {"title": title, "large": True}))

        body_raw = f"""<p>Bienvenue !</p>

        <p>Vous venez de créer un site utilisant le gestionnaire de contenus de l’État.</p>

        <p>Vous pouvez maintenant <a href="{ reverse('wagtailadmin_home')}">vous connecter dans l’administration</a>
        et personnaliser le site.</p>

        <p>En particulier, n'hésitez pas à :
        <ul>
            <li>Remplacer les paramètres par défaut du site dans Configuration > Configuration du site</li>
            <li>Remplacer le contenu de la page de mentions légales</li>
            <li>Remplacer le contenu de cette page d’accueil.</li>
        </ul>
        """

        body.append(("paragraph", RichText(body_raw)))

        root = Page.objects.get(slug="root")
        home_page = root.add_child(instance=ContentPage(title=title, body=body))

        # Define it as default
        site = Site.objects.first()

        site.root_page_id = home_page.id
        site.save()

        # Delete the original default page and get its slug
        original_home = Page.objects.get(slug="home")
        original_home.delete()

        home_page.slug = "home"
        home_page.save()
