from django.db import models


class Kind(models.TextChoices):
    FORMATION = "formation", "Formation"
    PARCOURS = "parcours", "Parcours"
    CYCLE = "cycle", "Cycle"
    SEMINAIRE = "séminaire", "Séminaire"
    UNIVERSITE = "université d'été", "Université d'été"
    PROGRAMME = "programme", "Programme"


class Attendance(models.TextChoices):
    ENLIGNE = "enligne", "En ligne"
    PRESENTIEL = "présentiel", "Présentiel"
    HYBRIDE = "hybride", "Hybride"
