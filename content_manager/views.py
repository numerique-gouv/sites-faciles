from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView
from unidecode import unidecode
from wagtail.models import Site

from content_manager.models import ContentPage, Tag


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

        breadcrumb = {
            "links": [],
            "current": _("Tags"),
        }

        context["sorted_tags"] = tags_by_first_letter
        context["breadcrumb"] = breadcrumb
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

        print(tag_slug)

        tag = get_object_or_404(Tag, slug=tag_slug)
        context["tag"] = tag

        # Use the homepage for context
        context["page"] = Site.objects.filter(is_default_site=True).first().root_page

        return context
