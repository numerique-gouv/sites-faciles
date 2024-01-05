from django import forms

from formations.models import TargetAudience, Theme


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
    target_audience = forms.ModelChoiceField(
        label="Public cible",
        queryset=TargetAudience.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "fr-select",
                "onchange": "this.form.submit()",
            }
        ),
        required=False,
    )
