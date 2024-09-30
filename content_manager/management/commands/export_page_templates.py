import json

from django.core.management.base import BaseCommand

from content_manager.services.import_export import TEMPLATES_DATA_FILE, ImportExportImages, ImportExportPage

SOURCE_URL = "https://sites-faciles.beta.numerique.gouv.fr/"


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Export template pages
        """

        page_ids = ["32", "37"]

        image_ids = []

        pages = {}

        for page_id in page_ids:
            page = ImportExportPage(SOURCE_URL, page_id)
            pages[page_id] = page.json_export
            image_ids += page.image_ids

        image_exporter = ImportExportImages(image_ids, SOURCE_URL)
        image_exporter.download_images()

        export_data = {"image_ids": image_ids, "pages": pages}
        with open(TEMPLATES_DATA_FILE, "w") as json_file:
            json.dump(export_data, json_file, indent=2)
