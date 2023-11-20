from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail_airtable.mixins import AirtableMixin

from formations.enums import Kind


class TargetAudience(models.Model):
    name = models.CharField("Nom", max_length=255)

    class Meta:
        verbose_name = "Public cible"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RelatedEntity(models.Model):
    name = models.CharField("Nom", max_length=255)
    airtable_id = models.CharField("Identifiant Airtable", max_length=255)

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name


class Theme(RelatedEntity):
    class Meta:
        verbose_name = "Famille thématique"
        verbose_name_plural = "Familles thématiques"


class Organizer(RelatedEntity):
    class Meta:
        verbose_name = "Entité organisatrice"
        verbose_name_plural = "Entités organisatrices"


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
    duration = models.CharField("Durée (min)", max_length=255, null=True, blank=True)
    registration_link = models.URLField("Lien d'inscription", max_length=255, blank=True)
    image_url = models.URLField("URL Image", null=True, blank=True)
    visible = models.TextField("Visible", blank=True)
    target_audience = ParentalManyToManyField(TargetAudience, verbose_name="Public cible", blank=True)
    themes = ParentalManyToManyField(Theme, verbose_name="Familles thématiques", blank=True)
    organizers = ParentalManyToManyField(Organizer, verbose_name="Entités organisatrices", blank=True)

    # Editor panels configuration (for debug)
    content_panels = Page.content_panels + [
        FieldPanel("name"),
        FieldPanel("kind"),
        FieldPanel("short_description"),
        FieldPanel("knowledge_at_the_end"),
        FieldPanel("duration"),
        FieldPanel("registration_link"),
        FieldPanel("image_url"),
        FieldPanel("target_audience"),
        FieldPanel("themes"),
        FieldPanel("organizers"),
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
            "Public cible": "target_audience",
            "Famille thématique": "themes",
            "Une formation proposée par": "organizers",
        }
        return mappings

    def get_export_fields(self):
        """
        Needed by AirtableMixin
        Should return a dictionary of the mapped fields from Airtable to the model.
        ie.
            {
                "airtable_column": self.airtable_column,
                "annual_fee": self.annual_fee,
            }
        """
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
            "Public cible": self.target_audience,
            "Famille thématique": self.themes,
            "Une formation proposée par": self.organizers,
        }

    class Meta:
        verbose_name = "Page Formation/Parcours"
