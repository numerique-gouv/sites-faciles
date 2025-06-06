# Create your views here.
from django.contrib.admin.utils import quote
from django.urls import reverse
from wagtail.admin.ui.components import Component
from wagtail.models import Site


class WelcomePanel(Component):
    order = 10

    def get_context_data(self, parent_content=None):
        site = Site.objects.filter(is_default_site=True).first()
        home_page = site.root_page
        home_page_edit = reverse("wagtailadmin_pages:edit", args=(quote(home_page.pk),))
        pages_list = reverse("wagtailadmin_explore", args=(quote(home_page.pk),))
        create_page_url = reverse("wagtailadmin_pages:add_subpage", args=(home_page.pk,))
        settings_url = reverse("wagtailsettings:edit", args=["content_manager", "cmsdsfrconfig", site.pk])
        main_menus = reverse("wagtailmenus:mainmenu_edit", args=[1])

        return {
            "home_page_edit": home_page_edit,
            "pages_list": pages_list,
            "create_page": create_page_url,
            "settings_url": settings_url,
            "main_menus": main_menus,
        }

    template_name = "./wagtailadmin/panels/welcome.html"


my_welcome_panel = WelcomePanel()
