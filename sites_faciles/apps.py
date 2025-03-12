from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SitesFacilesAppConfig(AppConfig):
    name = "sites_faciles"
    label = "sites_faciles"
    verbose_name = _("Sites Facile")
    default_auto_field = "django.db.models.AutoField"
