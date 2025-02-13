from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from proconnect.validators import sub_validator

User = get_user_model()


class UserOIDC(models.Model):
    # Join the user with the OIDC claims without affecting the user model
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)

    sub = models.CharField(
        _("sub"),
        help_text=_("Required. 255 characters or fewer. Letters, numbers, and @/./+/-/_/: characters only."),
        max_length=255,
        unique=True,
        validators=[sub_validator],
        blank=True,
        null=True,
    )

    siret = models.CharField(
        _("SIRET"),
        max_length=14,
        blank=True,
    )

    def __str__(self):
        return self.user.get_username()
