from django.db import models
from wagtail.models import Page
from formations.enums import Kind

class FormationPage(Page):
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
