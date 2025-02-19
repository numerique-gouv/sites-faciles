from django import forms
from django.utils.translation import gettext_lazy as _

from sites_faciles.config.forms.baseform import SitesFacilesBaseForm


class EventSearchForm(SitesFacilesBaseForm):
    """Main form for events page list."""

    date_from = forms.DateField(
        label=_("From…"),
        required=False,
        widget=forms.TextInput(attrs={"type": "date"}),
    )

    date_to = forms.DateField(
        label=_("To…"),
        required=False,
        widget=forms.TextInput(attrs={"type": "date"}),
    )
