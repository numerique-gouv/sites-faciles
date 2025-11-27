from django.apps import AppConfig


class FormsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "wagtail_dsfr.forms"
    label = "wagtail_dsfr_forms"
