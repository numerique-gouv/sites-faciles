from django.db import models
from django.utils.translation import gettext_lazy as _
from dsfr.constants import COLOR_CHOICES
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail.search import index

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
    header_with_title = models.BooleanField(_("Show title in header image?"), default=False)

    header_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header image"),
    )

    header_color_class = models.CharField(
        _("Background color"),
        choices=COLOR_CHOICES,
        null=True,
        blank=True,
        help_text=_("Uses the French Design System colors"),
    )

    header_large = models.BooleanField(_("Full width"), default=False)
    header_darken = models.BooleanField(_("Darken background image"), default=False)

    header_cta_text = models.CharField(
        _("Call to action text"),
        null=True,
        blank=True,
    )

    header_cta_label = models.CharField(
        _("Call to action label"),
        null=True,
        blank=True,
    )

    header_cta_link = models.URLField(
        _("Call to action link"),
        null=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body", heading=_("Body")),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, _("Common page configuration")),
        MultiFieldPanel(
            [
                FieldPanel("header_with_title"),
                FieldPanel("header_image"),
                FieldPanel("header_color_class"),
                FieldPanel("header_large"),
                FieldPanel("header_darken"),
                FieldPanel("header_cta_text"),
                FieldPanel("header_cta_label"),
                FieldPanel("header_cta_link"),
            ],
            heading=_("Header options"),
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        abstract = True
        verbose_name = _("Base page")
        verbose_name_plural = _("Base pages")
