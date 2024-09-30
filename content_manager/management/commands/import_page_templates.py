import json

from django.core.management.base import BaseCommand

from content_manager.services.import_export import TEMPLATES_DATA_FILE, ImportExportImages


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Import template pages
        """

        with open(TEMPLATES_DATA_FILE, "r") as json_file:
            page_templates_data = json.load(json_file)

        image_importer = ImportExportImages(page_templates_data["image_ids"])

        image_importer.import_images()
