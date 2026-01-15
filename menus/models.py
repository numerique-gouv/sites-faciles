# myapp/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Site, TranslatableMixin

from menus.blocks import FOOTER_BOTTOM_MENU_BLOCKS, MAIN_MENU_BLOCKS, TOP_MENU_BLOCKS


class TopMenu(TranslatableMixin, models.Model):
    """
    The menu in the top right corner of a site.
    """

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="top_menus",
        verbose_name=_("Site"),
        default=1,
        unique=True,
    )

    items = StreamField(
        TOP_MENU_BLOCKS,
        max_num=3,
        use_json_field=True,
        verbose_name=_("Menu items"),
        blank=True,
    )
    panels = [FieldPanel("site"), FieldPanel("items")]

    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Top menu")
        verbose_name_plural = _("Top menus")

    def __str__(self):
        return _("Top menu for site {hostname}").format(hostname=self.site.hostname)


class FooterBottomMenu(TranslatableMixin, models.Model):
    """
    The menu at the bottom part of the footer of a site.
    This menu contains the legal links: Terms of Service, Privacy Policy, etc.
    """

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="footerbottom_menus",
        verbose_name=_("Site"),
        default=1,
        unique=True,
    )

    items = StreamField(
        FOOTER_BOTTOM_MENU_BLOCKS,
        use_json_field=True,
        verbose_name=_("Menu items"),
        blank=True,
    )
    panels = [FieldPanel("site"), FieldPanel("items")]

    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Footer bottom menu")
        verbose_name_plural = _("Footer bottom menus")

    def __str__(self):
        return _("Footer bottom menu for site {hostname}").format(hostname=self.site.hostname)


class MainMenu(TranslatableMixin, models.Model):
    """
    The main menu of a site.
    """

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="main_menus",
        verbose_name=_("Site"),
        default=1,
        unique=True,
    )

    items = StreamField(
        MAIN_MENU_BLOCKS,
        use_json_field=True,
        verbose_name=_("Menu items"),
        blank=True,
    )
    panels = [FieldPanel("site"), FieldPanel("items")]

    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Main menu")
        verbose_name_plural = _("Main menus")

    def __str__(self):
        return _("Main menu for site {hostname}").format(hostname=self.site.hostname)
