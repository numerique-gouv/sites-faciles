from django.views.generic.list import ListView

from formations.form import FormationsFilterForm
from formations.models import FormationPage, Theme


class FormationsListView(ListView):
    model = FormationPage

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        form = FormationsFilterForm(self.request.GET or None)
        selected_themes = []
        if form.is_valid():
            selected_themes = form.cleaned_data.get("themes", [])

        context["breadcrumb_data"] = {"current": "Catalogue"}
        context["form"] = form

        # to put the right "aria-pressed" attributes on label
        context["selected_themes"] = {theme.name for theme in selected_themes}

        return context

    def get_queryset(self):
        queryset = super().get_queryset().live()
        form = FormationsFilterForm(self.request.GET or None)
        if form.is_valid():
            themes = form.cleaned_data.get("themes")
            if themes:
                queryset = queryset.filter(themes__in=themes)
        return queryset
