from django.contrib.admin.utils import quote
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.admin.ui.components import Component
from wagtail.models import Site
from wagtail.rich_text import LinkHandler


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html('\n<link rel="stylesheet" href="{}">', static("css/admin.css"))


@hooks.register("insert_editor_js")
def editor_js():
    return format_html('\n<script src="{}"></script>', static("js/admin_editor.js"))


@hooks.register("register_admin_menu_item")
def register_site_menu_item():
    return MenuItem(
        _("Visit site"),
        "/",
        icon_name="home",
        order=0,
    )


class UserbarPageAPILinkItem:
    """
    When on a Wagtail page, add a link to the Page API for admin users in the wagtail toolbar
    """

    def render(self, request) -> str:
        if hasattr(request, "_wagtail_route_for_request") and hasattr(request._wagtail_route_for_request, "page"):
            page = request._wagtail_route_for_request.page
            page_url = reverse("wagtailapi:pages:detail", kwargs={"pk": page.id})
            page_in_api_label = _("See page entry in API")
            if page and request.user.has_perm("wagtailadmin.access_admin"):
                return f"""<li class="w-userbar__item " role="presentation">
                            <a href="{page_url}" target="_parent" role="menuitem" tabindex="-1">
                                <svg class="icon icon-crosshairs w-action-icon" aria-hidden="true">
                                    <use href="#icon-crosshairs"></use>
                                </svg> {page_in_api_label}
                            </a>
                        </li>"""
        return ""


@hooks.register("construct_wagtail_userbar")
def add_page_api_link_item(request, items, page):
    return items.append(UserbarPageAPILinkItem())


class MainLinksPanel(Component):
    order = 50

    def render_html(self, parent_context):
        site = Site.objects.filter(is_default_site=True).first()
        home_page = site.root_page
        home_page_edit = reverse("wagtailadmin_pages:edit", args=(quote(home_page.pk),))

        pages_list = reverse("wagtailadmin_explore", args=(quote(home_page.pk),))

        return mark_safe(
            f"""<section class="panel">
                <ul>
                    <li>
                        <a href="{home_page_edit}">{_("Edit home page")}</a>
                    </li>
                    <li>
                        <a href="{pages_list}">{_("See pages")}</a>
                    </li>
                    <li>
                        <a href="/cms-admin/users/">{_("Manage users")}</a>
                    </li>
                </ul>
            </section>"""
        )


@hooks.register("construct_homepage_panels")
def add_main_links_panel(request, panels):
    panels.append(MainLinksPanel())


class NewWindowExternalLinkHandler(LinkHandler):
    identifier = "external"

    @classmethod
    def expand_db_attributes(cls, attrs):
        href = attrs["href"]
        # Let's add the target attr, and also rel="noopener" + noreferrer fallback.
        # See https://github.com/whatwg/html/issues/4078.
        new_window = _("(Opens a new window)")
        return f"""<a href="{escape(href)}" target="_blank" rel="noopener noreferrer">
                <span class="fr-sr-only">{new_window}</span> """


@hooks.register("register_rich_text_features")
def register_external_link(features):
    features.register_link_type(NewWindowExternalLinkHandler)
