from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase, override_settings
from wagtail.models import Site

from content_manager.models import ExternalServicesSettings
from content_manager.sentry import (
    SENTRY_DSN_CACHE_KEY,
    SENTRY_DSN_EMPTY_SENTINEL,
    bootstrap_sentry_from_db,
    get_sentry_dsn,
)

ENV_VAR_DSN = "https://envkey@sentry.example.com/1"
DB_DSN = "https://dbkey@sentry.example.com/2"
ANOTHER_DSN = "https://anotherkey@sentry.example.com/3"


class SentryBootstrapTestCase(TestCase):
    def setUp(self):
        cache.clear()
        ExternalServicesSettings.objects.all().delete()

    def tearDown(self):
        cache.clear()
        ExternalServicesSettings.objects.all().delete()

    @override_settings(SENTRY_DSN="")
    def test_bootstrap_does_not_call_init_when_no_dsn_at_all(self):
        """No DB record, no env var: bootstrap must not call init."""
        with patch("content_manager.sentry.sentry_sdk.init") as mock_init:
            bootstrap_sentry_from_db()
        mock_init.assert_not_called()

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_bootstrap_falls_back_to_env_var_when_db_has_no_record(self):
        """No DB record, env var set: bootstrap falls back to env var."""
        with patch("content_manager.sentry.sentry_sdk.init") as mock_init:
            bootstrap_sentry_from_db()
        mock_init.assert_called_once()
        self.assertEqual(mock_init.call_args[1]["dsn"], ENV_VAR_DSN, "Expected env var DSN")

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_bootstrap_writes_empty_sentinel_to_cache_when_db_has_no_record(self):
        with patch("content_manager.sentry.sentry_sdk.init"):
            bootstrap_sentry_from_db()
        self.assertEqual(
            cache.get(SENTRY_DSN_CACHE_KEY),
            SENTRY_DSN_EMPTY_SENTINEL,
            "Cache should hold the empty sentinel when the DB has no record",
        )

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_save_calls_init_with_db_dsn(self):
        """post_save signal: DB DSN takes priority over env var."""
        site = Site.objects.get(is_default_site=True)
        with patch("content_manager.sentry.sentry_sdk.init") as mock_init:
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": DB_DSN})
        mock_init.assert_called_once()
        self.assertEqual(mock_init.call_args[1]["dsn"], DB_DSN, "Expected DB DSN, not env var")

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_save_writes_db_dsn_to_cache(self):
        site = Site.objects.get(is_default_site=True)
        with patch("content_manager.sentry.sentry_sdk.init"):
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": DB_DSN})
        self.assertEqual(cache.get(SENTRY_DSN_CACHE_KEY), DB_DSN, "Cache should hold the DB DSN after save")

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_save_with_empty_dsn_writes_sentinel_to_cache(self):
        site = Site.objects.get(is_default_site=True)
        with patch("content_manager.sentry.sentry_sdk.init"):
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": ""})
        self.assertEqual(
            cache.get(SENTRY_DSN_CACHE_KEY),
            SENTRY_DSN_EMPTY_SENTINEL,
            "Cache should hold the empty sentinel when DSN is cleared",
        )

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_save_with_empty_dsn_shuts_down_sentry(self):
        """Saving an empty DSN must call init('') to shut the SDK down."""
        site = Site.objects.get(is_default_site=True)
        with patch("content_manager.sentry.sentry_sdk.init") as mock_init:
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": ""})
        mock_init.assert_called_once()
        self.assertEqual(mock_init.call_args[1]["dsn"], "", "Saving empty DSN should shut down Sentry with dsn=''")

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_bootstrap_calls_init_with_db_dsn_after_reboot(self):
        """Worker reboot: bootstrap reads DB DSN from scratch."""
        site = Site.objects.get(is_default_site=True)
        # Create the record (signal fires + populates cache), then clear cache to simulate reboot
        with patch("content_manager.sentry.sentry_sdk.init"):
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": DB_DSN})
        cache.clear()

        with patch("content_manager.sentry.sentry_sdk.init") as mock_init:
            bootstrap_sentry_from_db()

        mock_init.assert_called_once()
        self.assertEqual(mock_init.call_args[1]["dsn"], DB_DSN, "Expected DB DSN after reboot")

    @override_settings(SENTRY_DSN=ENV_VAR_DSN)
    def test_bootstrap_populates_cache_from_db_on_reboot(self):
        site = Site.objects.get(is_default_site=True)
        with patch("content_manager.sentry.sentry_sdk.init"):
            ExternalServicesSettings.objects.update_or_create(site=site, defaults={"sentry_dsn": DB_DSN})
        cache.clear()

        with patch("content_manager.sentry.sentry_sdk.init"):
            bootstrap_sentry_from_db()

        self.assertEqual(cache.get(SENTRY_DSN_CACHE_KEY), DB_DSN, "Cache should be repopulated from DB after reboot")

    def test_get_sentry_dsn_returns_cached_value_without_hitting_db(self):
        """Cache hit avoids DB query."""
        cache.set(SENTRY_DSN_CACHE_KEY, ANOTHER_DSN, timeout=None)
        with patch("content_manager.models.ExternalServicesSettings.objects") as mock_mgr:
            result = get_sentry_dsn()
        mock_mgr.first.assert_not_called()
        self.assertEqual(result, ANOTHER_DSN, "Should return cached DSN without hitting DB")

    def test_get_sentry_dsn_returns_empty_string_when_cache_has_sentinel(self):
        cache.set(SENTRY_DSN_CACHE_KEY, SENTRY_DSN_EMPTY_SENTINEL, timeout=None)
        with patch("content_manager.models.ExternalServicesSettings.objects") as mock_mgr:
            result = get_sentry_dsn()
        mock_mgr.first.assert_not_called()
        self.assertEqual(result, "", "Sentinel in cache should map to empty string without hitting DB")
