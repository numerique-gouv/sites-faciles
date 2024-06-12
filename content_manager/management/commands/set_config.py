import json
from os.path import isfile

from django.core.management.base import BaseCommand
from wagtail.models import Site

from content_manager.models import CmsDsfrConfig


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if isfile("config.json"):
            with open("config.json") as config_file:
                config_data = json.load(config_file)
                site = Site.objects.filter(is_default_site=True).first()
                config_data["site_id"] = site.id

                _config, created = CmsDsfrConfig.objects.get_or_create(id=1, defaults=config_data)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Config imported for {config_data.get('site_title', '')}"))
                else:
                    self.stdout.write(self.style.SUCCESS("Config already existing, data not imported."))
