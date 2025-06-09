import csv

from django.db.models import Q
from django.http import HttpResponse
from django.views.generic.list import ListView

from formations.form import FormationsFilterForm
from formations.models import FormationPage


class FormationsListView(ListView):
    model = FormationPage

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        form = FormationsFilterForm(self.request.GET or None)
        selected_themes = []
        selected_sub_themes = []
        if form.is_valid():
            selected_themes = form.cleaned_data.get("themes", [])
            selected_sub_themes = form.cleaned_data.get("sub_themes", [])

        context["breadcrumb_data"] = {"current": "Catalogue"}
        context["form"] = form

        # to put the right "aria-pressed" attributes on label
        context["selected_themes"] = {theme.name for theme in selected_themes}
        context["selected_sub_themes"] = {sub_theme.name for sub_theme in selected_sub_themes}
        return context

    def get_queryset(self):
        qs = super().get_queryset().live()
        form = FormationsFilterForm(self.request.GET or None)
        if form.is_valid():
            themes = form.cleaned_data.get("themes")
            if themes:
                qs = qs.filter(themes__in=themes)

            sub_themes = form.cleaned_data.get("sub_themes")
            if sub_themes:
                qs = qs.filter(sub_themes__in=sub_themes)

            target_audience = form.cleaned_data.get("target_audience")
            if target_audience:
                qs = qs.filter(target_audience__in=[target_audience])

            organizer = form.cleaned_data.get("organizer")
            if organizer:
                qs = qs.filter(organizers__in=[organizer])

            kind = form.cleaned_data.get("kind")
            if kind:
                qs = qs.filter(kind=kind)

            attendance = form.cleaned_data.get("attendance")
            if attendance:
                qs = qs.filter(attendance=attendance)

            search = form.cleaned_data.get("search")
            if search:
                qs = qs.filter(
                    Q(name__icontains=search)
                    | Q(short_description__icontains=search)
                    | Q(knowledge_at_the_end__icontains=search)
                )

        return qs

    def get(self, request, *args, **kwargs):
        if request.GET.get("export") == "csv":
            return self.export_csv()
        return super().get(request, *args, **kwargs)

    def export_csv(self):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="formations.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Intitulé",
                "Type",
                "Descriptif court",
                "Objectifs",
                "Durée",
                "Lien d'inscription",
                "Public cible",
                "Thématiques",
                "Sous-thématiques",
                "Organisateurs",
                "Modalité",
            ]
        )

        for formation in self.get_queryset():
            writer.writerow(
                [
                    formation.name,
                    formation.get_kind_display(),
                    formation.short_description,
                    formation.knowledge_at_the_end,
                    formation.duration,
                    formation.registration_link,
                    ", ".join(str(audience) for audience in formation.target_audience.all()),
                    ", ".join(str(theme) for theme in formation.themes.all()),
                    ", ".join(str(sub_theme) for sub_theme in formation.sub_themes.all()),
                    ", ".join(str(organizer) for organizer in formation.organizers.all()),
                    formation.get_attendance_display(),
                ]
            )

        return response
