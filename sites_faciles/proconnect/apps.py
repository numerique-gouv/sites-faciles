from django.apps import AppConfig


class ProconnectConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore
    name = "sites_faciles.proconnect"
    label = "sites_faciles_proconnect"
