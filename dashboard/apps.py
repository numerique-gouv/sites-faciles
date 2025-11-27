from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "wagtail_dsfr.dashboard"
    label = "wagtail_dsfr_dashboard"
