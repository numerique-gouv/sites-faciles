from django.views.generic.list import ListView

from formations.models import FormationPage


class FormationsListView(ListView):
    model = FormationPage

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["breadcrumb_data"] = {"current": "Catalogue"}
        return context

    def get_queryset(self):
        return super().get_queryset().live()
