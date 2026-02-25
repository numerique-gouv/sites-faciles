from django.apps import AppConfig


class ContentManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content_manager"

    def ready(self):
        from django.db.models.signals import post_save

        from content_manager.models import ExternalServicesSettings
        from content_manager.sentry import bootstrap_sentry_from_db, invalidate_sentry_cache

        post_save.connect(
            invalidate_sentry_cache,
            sender=ExternalServicesSettings,
            dispatch_uid="external_services_settings_post_save",
        )

        bootstrap_sentry_from_db()
