from django.db import models
from django.db.models import Count


class TagManager(models.Manager):
    def tags_with_usecount(self, min_count=0):
        return self.annotate(usecount=Count("contentpage")).filter(usecount__gte=min_count)
