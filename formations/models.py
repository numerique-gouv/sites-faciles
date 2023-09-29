from django.db import models
from wagtail.models import Page
from formations.enums import Kind
from wagtail.admin.panels import FieldPanel
from wagtail_airtable.mixins import AirtableMixin


class FormationPage(AirtableMixin, Page):
    name = models.CharField("Intitulé", max_length=255)
    kind = models.CharField(
        "Type",
        max_length=20,
        choices=Kind.choices,
        blank=True,
    )
    short_description = models.TextField("Descriptif court", blank=True)
    knowledge_at_the_end = models.TextField("À la fin, vous saurez", blank=True)
    duration = models.IntegerField("Durée (min)", null=True, blank=True)
    registration_link = models.URLField("Lien d'inscription", max_length=255, blank=True)
    image_url = models.URLField("URL Image", null=True, blank=True)
    visible = models.TextField("Visible", blank=True)

    # Editor panels configuration (for debug)
    content_panels = Page.content_panels + [
        FieldPanel("name"),
        FieldPanel("kind"),
        FieldPanel("short_description"),
        FieldPanel("knowledge_at_the_end"),
        FieldPanel("duration"),
        FieldPanel("registration_link"),
        FieldPanel("image_url"),
    ]

    @classmethod
    def map_import_fields(cls):
        mappings = {
            "Intitulé": "title",
            "Intitulé à faire apparaître": "name",
            "Type": "kind",
            "Descriptif court": "short_description",
            "A la fin de cette formation / ce parcours, vous saurez :": "knowledge_at_the_end",
            "Durée": "duration",
            "Lien d'inscription": "registration_link",
            "URL image": "image_url",
            "Visible": "visible",
        }
        return mappings

    def get_export_fields(self):
        return {
            "Intitulé": self.title,
            "Intitulé à faire apparaître": self.name,
            "Type": self.kind,
            "Descriptif court": self.short_description,
            "A la fin de cette formation / ce parcours, vous saurez :": self.knowledge_at_the_end,
            "Durée": self.duration,
            "Lien d'inscription": self.registration_link,
            "URL image": self.image_url,
            "Visible": self.visible,
        }

    class Meta:
        verbose_name = "Page Formation/Parcours"
