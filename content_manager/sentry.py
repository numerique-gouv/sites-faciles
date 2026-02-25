import os

import sentry_sdk
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

SENTRY_DSN_CACHE_KEY = "sentry_dsn_from_db"
SENTRY_DSN_EMPTY_SENTINEL = "__empty__"


def _init_sentry(dsn: str) -> None:
    sentry_sdk.init(
        dsn=dsn,
        send_default_pii=True,
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
    )


def get_sentry_dsn() -> str:
    """Return the Sentry DSN from cache, or DB on cache miss (inspired by django-constance pattern).

    Cache holds either a real DSN string or SENTRY_DSN_EMPTY_SENTINEL when the DB
    has no record. A return of None from cache.get() means a genuine cache miss.
    """
    cached = cache.get(SENTRY_DSN_CACHE_KEY)

    if cached is not None:
        return "" if cached == SENTRY_DSN_EMPTY_SENTINEL else cached

    # Cache miss - query the DB
    from django.db import OperationalError, ProgrammingError

    from content_manager.models import ExternalServicesSettings

    try:
        settings_obj = ExternalServicesSettings.objects.first()
        dsn = (settings_obj.sentry_dsn or "") if settings_obj else ""
    except (OperationalError, ProgrammingError):
        return ""

    # Populate cache so subsequent calls never touch the DB
    cache.set(
        SENTRY_DSN_CACHE_KEY,
        dsn if dsn else SENTRY_DSN_EMPTY_SENTINEL,
        timeout=None,  # infinite - invalidated by post_save signal
    )
    return dsn


def bootstrap_sentry_from_db() -> None:
    """Called from AppConfig.ready() on every worker startup.

    Priority: DB DSN > SENTRY_DSN env var > no-op.
    Catches DB errors so the app starts cleanly before migrations have run.
    """
    from django.db import OperationalError, ProgrammingError

    try:
        dsn = get_sentry_dsn()
    except (OperationalError, ProgrammingError):
        dsn = ""

    if not dsn:
        # Fall back to the env var when the DB has no record
        from django.conf import settings as django_settings

        dsn = getattr(django_settings, "SENTRY_DSN", "")

    if dsn:
        _init_sentry(dsn)


@receiver(
    post_save, sender="content_manager.ExternalServicesSettings", dispatch_uid="external_services_settings_post_save"
)
def invalidate_sentry_cache(sender, instance, **kwargs) -> None:
    """post_save signal receiver: update cache and re-init (or shut down) Sentry."""
    new_dsn = instance.sentry_dsn or ""

    # Delete then immediately repopulate so the cache is consistent without
    # requiring another DB round-trip on the next read.
    cache.delete(SENTRY_DSN_CACHE_KEY)
    cache.set(
        SENTRY_DSN_CACHE_KEY,
        new_dsn if new_dsn else SENTRY_DSN_EMPTY_SENTINEL,
        timeout=None,
    )

    # Passing an empty string shuts the SDK down, allowing the admin to
    # disable Sentry at runtime without a worker restart.
    _init_sentry(new_dsn)
