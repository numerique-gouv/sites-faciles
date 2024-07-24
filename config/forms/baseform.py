from dsfr.forms import DsfrBaseForm


class SitesFacilesBaseForm(DsfrBaseForm):
    # Subclassing the Dsfr base form to set autofocus on the first error found when applicable

    template_name = "dsfr/form_snippet.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_autofocus_on_first_error()
