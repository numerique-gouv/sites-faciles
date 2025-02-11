import unicodedata

from django.contrib.auth import get_user_model

from proconnect.models import UserOIDC

User = get_user_model()


def generate_username_as_email(email):
    """
    Allows to use the email as the username.

    To use it, set OIDC_USERNAME_ALGO = "dashboard.authentication.utils.generate_username_as_email" in settings.py.

    Using Python 3 and Django 1.11+, usernames can contain alphanumeric (ascii and unicode),
    _, @, +, .and - characters. So we normalize it and slice at 150 characters.
    """
    return unicodedata.normalize("NFKC", email)[:150]


def get_user_by_sub_or_email(sub, email):
    """
    Get the user by its sub, and if not found, try by email.
    If the user is then found, create the UserOIDC entry.
    """
    user_oidc = UserOIDC.objects.filter(sub=sub).first()
    if user_oidc:
        return user_oidc.user

    user = User.objects.filter(email=email).first()

    if user:
        user_oidc = UserOIDC.objects.create(user=user, sub=sub)
        user_oidc.save()

    return user
