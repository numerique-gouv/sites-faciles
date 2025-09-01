from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView
from unidecode import unidecode
from wagtail.models import Site

from sites_faciles.content_manager.models import ContentPage, Tag


class SearchResultsView(ListView):
    model = ContentPage
    template_name = "content_manager/search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q", None)
        if query:
            object_list = ContentPage.objects.live().search(query)

        else:
            object_list = ContentPage.objects.none()
        return object_list

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context


class TagsListView(TemplateView):
    template_name = "content_manager/tags_list_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        tags = Tag.objects.tags_with_usecount(1)

        tags_by_first_letter = {}
        for tag in tags:
            first_letter = unidecode(tag.slug[0].upper())
            if first_letter not in tags_by_first_letter:
                tags_by_first_letter[first_letter] = []
            tags_by_first_letter[first_letter].append(tag)

        context["sorted_tags"] = tags_by_first_letter

        title = _("Tags")
        context["title"] = title
        context["breadcrumb"] = {
            "links": [],
            "current": title,
        }
        context["search_description"] = _("List of all the tags.")

        return context


class TagView(ListView):
    template_name = "content_manager/tag_page.html"
    model = ContentPage
    paginate_by = 10

    def get_queryset(self, **kwargs):
        tag_slug = self.kwargs.get("tag")
        return ContentPage.objects.filter(tags__slug=tag_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get("tag")

        tag = get_object_or_404(Tag, slug=tag_slug)
        context["tag"] = tag

        title = _("Pages tagged with {tag}").format(tag=tag.name)
        context["title"] = title
        context["breadcrumb"] = {
            "links": [
                {"url": reverse("global_tags_list"), "title": _("Tags")},
            ],
            "current": title,
        }

        context["search_description"] = _("List of pages tagged with {tag}").format(tag=tag.name)

        return context


class SiteMapView(TemplateView):
    """
    Readable sitemap for accessibility
    (different than the SEO-oriented sitemap.xml)
    """

    template_name = "content_manager/sitemap_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = Site.find_for_request(self.request)
        context["home_page"] = site.root_page

        title = _("Sitemap")
        context["title"] = title

        context["breadcrumb"] = {
            "links": [],
            "current": title,
        }
        return context
