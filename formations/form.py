from django import forms

from formations.models import Theme


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
