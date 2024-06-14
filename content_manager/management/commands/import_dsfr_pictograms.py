import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.images.models import Image

from content_manager.utils import get_or_create_collection, import_image


class Command(BaseCommand):
    help = """Import all the pictograms from the DSFR"""

    def handle(self, *args, **kwargs):
        call_command("collectstatic", interactive=False)

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

                image_exists = Image.objects.filter(title=full_image_title).count()

                if image_exists:
                    print(f"A file named {full_image_title} already exists, skipping")
                else:
                    image = import_image(
                        full_path=os.path.join(folder_path, filename),
                        title=full_image_title,
                    )

                    collection = get_or_create_collection("Pictogrammes DSFR")

                    image.collection = collection
                    image.save()

                    image.tags.add("DSFR")
                    image.tags.add("Pictogrammes")
                    image.tags.add(folder_title)
                    print(f"File {full_image_title} imported")
