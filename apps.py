from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WagtailDsfrAppConfig(AppConfig):
    name = "wagtail_dsfr"
    label = "wagtail_dsfr"
    verbose_name = _("Wagtail Dsfr")
    default_auto_field = "django.db.models.AutoField"
