from django.core.management.base import BaseCommand

from content_manager.services.import_export import ImportExportImage, ImportExportPage

SOURCE_URL = "https://sites-faciles.beta.numerique.gouv.fr/"


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Export template pages
        """

        page_ids = ["32", "37"]

        image_ids = []

        for page_id in page_ids:
            page = ImportExportPage(SOURCE_URL, page_id)
            image_ids += page.image_ids

        image_exporter = ImportExportImage(SOURCE_URL, image_ids)
        image_exporter.download_images()
