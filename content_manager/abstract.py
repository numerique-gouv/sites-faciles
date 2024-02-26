from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page

from content_manager.blocks import STREAMFIELD_COMMON_BLOCKS


class SitesFacilesBasePage(Page):
    """
    This class defines a base page model that will be used
    by all pages in Sites Faciles
    """

    body = StreamField(
        STREAMFIELD_COMMON_BLOCKS,
        blank=True,
        use_json_field=True,
    )
    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header image"),
    )

    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("body", heading=_("Body")),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        abstract = True
        verbose_name = _("Base page")
        verbose_name_plural = _("Base pages")
