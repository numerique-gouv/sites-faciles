from django.db import models


class Kind(models.TextChoices):
    FORMATION = "formation", "Formation"
    PARCOURS = "parcours", "Parcours"
