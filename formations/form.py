from django import forms

from formations.enums import Attendance, Kind
from formations.models import FormationPage, Organizer, SubTheme, TargetAudience, Theme


class FormationsFilterForm(forms.Form):
    themes = forms.ModelMultipleChoiceField(
        label="Thématiques",
        queryset=Theme.objects.filter(formationpage__isnull=False).distinct(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "form-checkbox fr-input vh",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    sub_themes = forms.ModelChoiceField(
        label="Sous-thématiques",
        queryset=SubTheme.objects.filter(formationpage__isnull=False).distinct(),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the selected themes from the form data
        selected_themes = self.data.getlist("themes")

        # Filter sub_themes based on selected themes through FormationPage
        if selected_themes:
            # Get FormationPages that have the selected themes
            formation_pages_with_themes = FormationPage.objects.filter(themes__in=selected_themes)
            # Filter sub_themes to only those that appear in these FormationPages
            self.fields["sub_themes"].queryset = SubTheme.objects.filter(
                formationpage__in=formation_pages_with_themes
            ).distinct()

    target_audience = forms.ModelChoiceField(
        label="Public visé",
        queryset=TargetAudience.objects.filter(formationpage__isnull=False).distinct(),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    organizer = forms.ModelChoiceField(
        label="Structure organisatrice",
        queryset=Organizer.objects.filter(formationpage__isnull=False).distinct(),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    kind = forms.ChoiceField(
        label="Type de formation",
        choices=[("", "Tous")] + list(Kind.choices),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    attendance = forms.ChoiceField(
        label="En ligne/Présentiel/Hybride",
        choices=[("", "Tous")] + list(Attendance.choices),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )

    search = forms.CharField(
        label="Rechercher par mot-clé",
        widget=forms.TextInput(
            attrs={
                "class": "fr-input",
            }
        ),
        required=False,
    )
