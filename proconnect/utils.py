from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from proconnect.models import UserOIDC

User = get_user_model()


def get_user_by_sub_or_email(sub: str, email: str, siret: str):
    """
    Get the user by its sub, and if not found, try by email.
    If the user is then found, create the UserOIDC entry.
    """
    user_oidc = UserOIDC.objects.filter(sub=sub).first()
    if user_oidc:
        return user_oidc.user

    user = User.objects.filter(email=email).first()

    if user:
        user_oidc = UserOIDC.objects.create(user=user, sub=sub, siret=siret)
        user_oidc.save()

    return user


def email_domain_whitelist(user_info: dict) -> dict:
    """
    Example method of a filter for ProConnect.

    Checks the email domain and returns True if it is a gov domain.

    For now just checking if it ends in .gouv.fr but this method should be able to take a
    proper whitelist at some point
    """
    email = user_info.get("email")
    if email.endswith(".gouv.fr"):
        result = {"status": "success"}
    else:
        result = {"status": "error", "message": _("User email domain not allowed.")}

    return result
