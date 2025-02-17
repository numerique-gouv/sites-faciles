from django.contrib.auth import get_user_model
from wagtail.test.utils import WagtailPageTestCase

from proconnect.models import UserOIDC, WhitelistedEmailDomain
from proconnect.utils import email_domain_basic_whitelist, email_domain_db_whitelist, get_user_by_sub_or_email

User = get_user_model()


class ProconnectUtilsTestCase(WagtailPageTestCase):
    def setUp(self):
        self.local_user = User.objects.create_superuser("local_user@test.test", "local_user@test.test", "pass")

        self.oidc_user = User.objects.create_superuser("oic_user@test.test", "oic_user@test.test", "pass")
        UserOIDC.objects.create(user=self.oidc_user, sub="knownsub", siret="13002526500013")

        WhitelistedEmailDomain.objects.create(domain="beta.gouv.fr")

    def test_get_user_by_sub_or_email_oidc_user(self):
        result = get_user_by_sub_or_email(sub="knownsub", email=self.oidc_user, siret="13002526500013")
        self.assertEqual(self.oidc_user, result)

    def test_get_user_by_sub_or_email_local_user(self):
        self.assertEqual(UserOIDC.objects.count(), 1)

        result = get_user_by_sub_or_email(sub="newsub", email=self.local_user, siret="13002526500013")

        self.assertEqual(self.local_user, result)
        self.assertEqual(UserOIDC.objects.count(), 2)

    def test_email_domain_basic_whitelist_allowed(self):
        result = email_domain_basic_whitelist({"email": "allowed.user@beta.gouv.fr"})
        self.assertEqual(result["status"], "success")

    def test_email_domain_basic_whitelist_not_allowed(self):
        result = email_domain_basic_whitelist({"email": "disallowed.user@example.fr"})
        self.assertEqual(result["status"], "error")

    def test_email_domain_db_whitelist_allowed(self):
        result = email_domain_db_whitelist({"email": "allowed.user@beta.gouv.fr"})
        self.assertEqual(result["status"], "success")

    def test_email_domain_db_whitelist_not_allowed(self):
        result = email_domain_db_whitelist({"email": "disallowed.user@example.fr"})
        self.assertEqual(result["status"], "error")
