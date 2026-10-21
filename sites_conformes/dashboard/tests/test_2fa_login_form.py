from unittest import mock

from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django_otp.oath import totp
from django_otp.plugins.otp_totp.models import TOTPDevice
from wagtail_2fa.forms import TokenForm

User = get_user_model()


@override_settings(WAGTAIL_2FA_REQUIRED=True)
class OtpFormSignOutButtonTest(TestCase):
    """
    Regression test: on the "enter your two-factor authentication code"
    screen, the "Sign out" button must work even though the otp_token field
    is empty and marked ``required``. Without ``formnovalidate`` on that
    button, browsers block the form submission client-side (native HTML5
    validation), so clicking "Sign out" silently does nothing and the user
    stays stuck on the code-entry screen.
    """

    def setUp(self):
        self.user = User.objects.create_superuser("alice", "alice@test.test", "pass")
        TOTPDevice.objects.create(user=self.user, name="Device", confirmed=True)
        self.client.login(username="alice", password="pass")

    def test_sign_out_button_skips_client_side_validation(self):
        response = self.client.get(reverse("wagtail_2fa_auth"))
        content = response.content.decode()

        sign_out_button_start = content.index('formaction="')
        button_markup = content[max(0, sign_out_button_start - 200) : sign_out_button_start]

        self.assertIn("formnovalidate", button_markup)

    def test_sign_out_button_logs_the_user_out(self):
        """
        Simulates the browser submitting the "Sign out" button: a POST to
        wagtailadmin_logout with no otp_token, since the whole point of
        formnovalidate is to let that submission through despite the empty
        required field. The user must actually be logged out, not bounced
        back to the code-entry screen.
        """
        response = self.client.post(reverse("wagtailadmin_logout"))

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


@override_settings(WAGTAIL_2FA_REQUIRED=True)
class OtpFormCustomTextTest(TestCase):
    """
    The "enter your two-factor authentication code" screen customizes the
    default wagtail-2fa copy: it adds a reminder paragraph pointing users to
    their authenticator app, and gives the otp_token field an explicit label
    and help text (the field otherwise falls back to Django's untranslated
    auto-generated label "Otp token" with no help text).
    """

    def setUp(self):
        self.user = User.objects.create_superuser("alice", "alice@test.test", "pass")
        TOTPDevice.objects.create(user=self.user, name="Device", confirmed=True)
        self.client.login(username="alice", password="pass")

    def test_reminder_paragraph_is_shown(self):
        response = self.client.get(reverse("wagtail_2fa_auth"))
        content = response.content.decode()

        self.assertIn(
            "Ouvrez votre application d’authentification (Aegis, Bitwarden, Google Authenticator, "
            "Microsoft Authenticator...) pour obtenir le code à entrer ci-dessous.",
            content,
        )

    def test_otp_field_has_custom_label_and_help_text(self):
        """
        The site's default language is French, so these msgids (shared with
        the add-device form, see device_form.html) render as their existing
        French translations rather than verbatim.
        """
        response = self.client.get(reverse("wagtail_2fa_auth"))
        content = response.content.decode()

        self.assertIn("Code de sécurité", content)
        self.assertIn("Entrez le code à six chiffres affiché dans l’application.", content)
        self.assertNotIn("Otp token", content)


@override_settings(WAGTAIL_2FA_REQUIRED=True)
class OtpFormVerifyTokenTest(TestCase):
    """
    Regression test: since django-otp 1.7.4, a login form without an
    ``otp_device`` field (such as wagtail-2fa's TokenForm) rejected every
    code with a ``device_required`` error, rendered as "Code invalide".
    See patch_wagtail_2fa_token_form_device_selection in monkey_patches.py.
    """

    def setUp(self):
        self.user = User.objects.create_superuser("alice", "alice@test.test", "pass")
        self.device = TOTPDevice.objects.create(user=self.user, name="Device", confirmed=True)
        self.client.login(username="alice", password="pass")
        self.url = reverse("wagtail_2fa_auth")

    def _token(self, device):
        return str(totp(device.bin_key)).zfill(6)

    def test_valid_code_verifies_the_session(self):
        response = self.client.post(self.url, {"otp_token": self._token(self.device)})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("otp_device_id"), self.device.persistent_id)

    def test_wrong_code_is_rejected(self):
        wrong_token = str((int(self._token(self.device)) + 1) % 1000000).zfill(6)

        response = self.client.post(self.url, {"otp_token": wrong_token})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Code invalide")
        self.assertNotIn("otp_device_id", self.client.session)

    def test_code_from_any_confirmed_device_is_accepted(self):
        second_device = TOTPDevice.objects.create(user=self.user, name="Device 2", confirmed=True)

        response = self.client.post(self.url, {"otp_token": self._token(second_device)})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get("otp_device_id"), second_device.persistent_id)


@override_settings(WAGTAIL_2FA_REQUIRED=True)
class OtpFormUnexpectedErrorReportingTest(TestCase):
    """
    The code-entry screen shows "Code invalide" for any form error, so
    unexpected ones (as opposed to a wrong or missing code) are logged at
    ERROR level for Sentry to pick up.
    See patch_wagtail_2fa_token_form_report_unexpected_errors in monkey_patches.py.
    """

    logger_name = "sites_conformes.dashboard.monkey_patches"

    def setUp(self):
        self.user = User.objects.create_superuser("alice", "alice@test.test", "pass")
        TOTPDevice.objects.create(user=self.user, name="Device", confirmed=True)
        self.client.login(username="alice", password="pass")
        self.url = reverse("wagtail_2fa_auth")

    def test_unexpected_error_is_logged(self):
        error = forms.ValidationError("Please select a device.", code="device_required")

        with (
            mock.patch.object(TokenForm, "_verify_token", side_effect=error),
            self.assertLogs(self.logger_name, level="ERROR") as logs,
        ):
            response = self.client.post(self.url, {"otp_token": "123456"})

        self.assertContains(response, "Code invalide")
        self.assertEqual(len(logs.records), 1)
        self.assertIn("device_required", logs.output[0])
        self.assertIn(str(self.user.pk), logs.output[0])

    def test_wrong_code_is_not_logged(self):
        with self.assertNoLogs(self.logger_name, level="ERROR"):
            response = self.client.post(self.url, {"otp_token": "000000"})

        self.assertContains(response, "Code invalide")

    def test_missing_code_is_not_logged(self):
        with self.assertNoLogs(self.logger_name, level="ERROR"):
            response = self.client.post(self.url, {"otp_token": ""})

        self.assertEqual(response.status_code, 200)
