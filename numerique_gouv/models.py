from django.utils.translation import gettext_lazy as _

from numerique_gouv.abstract import NumeriqueBasePage


class NumeriquePage(NumeriqueBasePage):
    class Meta:
        verbose_name = _("Numerique page")
