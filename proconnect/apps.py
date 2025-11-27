from django.apps import AppConfig


class ProconnectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "wagtail_dsfr.proconnect"
    label = "wagtail_dsfr_proconnect"
