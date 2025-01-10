import os

from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from content_manager.services.accessors import get_or_create_collection
from content_manager.utils import import_image


class Command(BaseCommand):
    help = """
    Import all the pictograms from the DSFR.

    Should only be launched if the statics have been collected at least once.
    """

    def handle(self, *args, **kwargs):
        picto_root = "staticfiles/dsfr/dist/artwork/pictograms/"
        picto_folders = os.listdir(picto_root)
        picto_folders.sort()

        for folder in picto_folders:
            folder_path = os.path.join(picto_root, folder)
            files = os.listdir(folder_path)
            files.sort()

            folder_title = folder.capitalize()

            for filename in files:
                base_file_title = filename.split(".")[0].replace("-", " ").title()
                full_image_title = f"Pictogrammes DSFR — {folder_title} — {base_file_title}"

                image_exists = Image.objects.filter(title=full_image_title).first()
                if image_exists:
                    file_hash = image_exists.get_file_hash()
                    print(f"A file named {full_image_title} already exists, skipping (file_hash: {file_hash})")
                else:
                    image = import_image(
                        full_path=os.path.join(folder_path, filename),
                        title=full_image_title,
                    )

                    collection = get_or_create_collection("Pictogrammes DSFR")

                    image.collection = collection
                    image.save()
                    image.get_file_hash()

                    image.tags.add("DSFR")
                    image.tags.add("Pictogrammes")
                    image.tags.add(folder_title)
                    print(f"File {full_image_title} imported")
