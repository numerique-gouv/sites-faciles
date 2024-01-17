from django.views.generic import ListView

from content_manager.models import ContentPage


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
