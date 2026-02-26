from django.apps import AppConfig


class ContentManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content_manager"

    def ready(self):
        from content_manager.sentry import bootstrap_sentry_from_db, invalidate_sentry_cache  # noqa: F401

        bootstrap_sentry_from_db()
