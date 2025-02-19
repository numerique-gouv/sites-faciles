from django.core.management.base import BaseCommand

from sites_faciles.blog.services.import_export import ImportPages


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """
        Import template pages
        """

        page_importer = ImportPages()
        page_importer.import_pages()
