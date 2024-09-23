from django.core.management.base import BaseCommand

from content_manager.services.import_export import ImportExportPage

SOURCE_URL = "https://sites-faciles.beta.numerique.gouv.fr/"


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Import template pages
        """

        page_ids = ["32", "37"]

        for page_id in page_ids:
            page = ImportExportPage(SOURCE_URL, page_id)
            # pprint(page.source_body)
            print(page.image_ids)
