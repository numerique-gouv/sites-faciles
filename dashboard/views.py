# Create your views here.
import json

import requests
from django.contrib.admin.utils import quote
from django.urls import reverse
from wagtail.admin.ui.components import Component
from wagtail.models import Site
from wagtailmenus.models import MainMenu


class ShortcutsPanel(Component):
    order = 50

    def get_context_data(self, parent_content=None):
        site = Site.objects.filter(is_default_site=True).first()
        home_page = site.root_page
        home_page_edit = reverse("wagtailadmin_pages:edit", args=(quote(home_page.pk),))
        pages_list = reverse("wagtailadmin_explore", args=(quote(home_page.pk),))
        create_page_url = reverse("wagtailadmin_pages:add_subpage", args=(home_page.pk,))
        settings_url = reverse("wagtailsettings:edit", args=["content_manager", "cmsdsfrconfig", site.pk])
        main_menu = MainMenu.objects.filter(site=site).first()
        main_menu_url = f"/cms-admin/wagtailmenus/mainmenu/edit/{main_menu.pk}/"
        return {
            "site": site,
            "home_page_edit": home_page_edit,
            "pages_list": pages_list,
            "create_page": create_page_url,
            "settings_url": settings_url,
            "main_menus": main_menu_url,
        }

    template_name = "wagtailadmin/home/panels/_main_links.html"


shortcuts_panel = ShortcutsPanel()


class TutorialsPanel(Component):
    order = 300

    def get_context_data(self, parent_content=None):
        res = requests.get("https://sites-faciles.beta.numerique.gouv.fr/api/v2/pages/?child_of=107&fields=*")
        response = json.loads(res.text)
        tutorials = [
            {
                "title": tutorial_page["title"],
                # "image": tutorial_page.get("meta", {}).get("preview_image_render", ""),
                "url": tutorial_page["meta"]["html_url"],
            }
            for tutorial_page in response["items"]
        ]
        return {"tutorials": tutorials}

    template_name = "wagtailadmin/home/panels/_tutorials.html"


tutorials_panel = TutorialsPanel()
