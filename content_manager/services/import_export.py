import copy
import json
import os
from io import BytesIO
from urllib.request import urlretrieve

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.images import ImageFile
from django.utils import timezone
from wagtail.images.models import Image
from wagtail.utils.file import hash_filelike

from content_manager.utils import get_or_create_collection

PAGE_TEMPLATES_ROOT = settings.BASE_DIR / "content_manager/page_templates"
TEMPLATES_DATA_FILE = PAGE_TEMPLATES_ROOT / "pages_data.json"
IMAGES_FOLDER = PAGE_TEMPLATES_ROOT / "img"
IMAGES_DATA_FILE = PAGE_TEMPLATES_ROOT / "image_data.json"

User = get_user_model()


class ImportExportPage:
    """
    Generic class for import/export of a ContentPage from a wagtail instance
    """

    def __init__(self, source_site, source_page_id) -> None:
        self.source_site = source_site
        self.source_page_id = source_page_id
        self.source_content = self.get_content_from_source_page()
        self.source_body = self.source_content["body"]
        self.user = User.objects.filter(is_superuser=True).first()

        self.content = copy.deepcopy(self.source_content)
        self.content["body"] = remove_block_ids(self.source_body)
        self.content.pop("tags", None)
        self.clear_meta_keys()

        self.images = {}
        self.image_ids = []
        self.get_source_images()

    @property
    def json_export(self) -> dict:
        return self.content

    @property
    def source_page_api_url(self):
        return f"{self.source_site}api/v2/pages/{self.source_page_id}/"

    def get_content_from_source_page(self):
        response = requests.get(self.source_page_api_url)
        return response.json()

    def get_source_images(self) -> None:
        """
        Get a list of images present in the source content.
        """

        # Header image
        header_image = self.source_content.get("header_image", None)
        if header_image:
            header_image["local_image"] = None
            img_id = header_image["id"]
            self.images[img_id] = header_image

        # Images from the body
        self.locate_image_ids(self.source_body)
        self.image_ids = list(set(self.image_ids))

    def locate_image_ids(self, json_object):
        if isinstance(json_object, dict) and json_object:
            for key, value in json_object.items():
                if key in ["image", "bg_image"] and value:
                    self.image_ids.append(value)
                else:
                    self.locate_image_ids(value)

        elif isinstance(json_object, list) and json_object:
            for item in json_object:
                self.locate_image_ids(item)

    def clear_meta_keys(self):
        keys = ["parent", "seo_title", "search_description"]
        for key in keys:
            self.content["meta"].pop(key, None)


class ImportExportImages:
    """
    Generic class for import/export of an Image from a wagtail instance
    """

    def __init__(self, image_ids, source_site=None) -> None:
        self.image_ids = set(image_ids)
        self.source_site = source_site

        # Create the folder for the files if it doesn't exist
        os.makedirs(IMAGES_FOLDER, exist_ok=True)

        # Create the collection if it doesn't exit
        self.collection = get_or_create_collection("Images des modèles de page")

        self.image_data = self.get_image_data()

    def get_image_data(self) -> dict:
        if os.path.isfile(IMAGES_DATA_FILE):
            with open(IMAGES_DATA_FILE, "r") as json_file:
                image_data = json.load(json_file)
        else:
            image_data = {}

        return image_data

    def source_image_api_url(self, image_id: int) -> str:
        return f"{self.source_site}api/v2/images/{image_id}/"

    def get_content_from_source_image(self, image_id: int) -> dict:
        response = requests.get(self.source_image_api_url(image_id))
        return response.json()

    def download_images(self) -> None:
        for i in self.image_ids:
            i = str(i)
            image = self.get_content_from_source_image(i)

            if i not in self.image_data:
                self.image_data[i] = {}
            self.image_data[i]["meta"] = image["meta"]
            self.image_data[i]["title"] = image["title"]

            image_url = image["meta"]["download_url"]
            image_name = image_url.split("?")[0].split("/")[-1]

            # No need to export the pictograms, as they should already be present
            if "Pictogrammes_DSFR" in image_name:
                pictogram_title = image_name.replace("__", " — ").replace("_", " ")
                self.image_data[i]["filename"] = pictogram_title
                self.image_data[i]["is_pictogram"] = True

            else:
                urlretrieve(image_url, IMAGES_FOLDER / image_name)
                self.image_data[i]["filename"] = image_name
                self.image_data[i]["is_pictogram"] = False

        with open(IMAGES_DATA_FILE, "w") as json_file:
            json.dump(self.image_data, json_file, indent=2)

    def import_images(self) -> None:
        for i in self.image_ids:
            i = str(i)
            image_data = self.image_data[i]
            filename = image_data["filename"]

            if image_data["is_pictogram"]:
                pictogram = Image.objects.filter(title=filename).first()
                image_data["local_id"] = pictogram.id
            else:
                image = self.get_or_create_image(image_data)
                image_data["local_id"] = image.id

        print(self.image_data)

    def get_or_create_image(self, image_data) -> Image:
        filename = image_data["filename"]
        imported_filename = f"template_image_{filename.lower()}"
        title = image_data["title"]

        with open(IMAGES_FOLDER / filename, "rb") as image_file:
            file_hash = hash_filelike(image_file)

            image = Image.objects.filter(file_hash=file_hash).first()

            if not image:
                image = Image(
                    file=ImageFile(BytesIO(image_file.read()), name=imported_filename),
                    title=title,
                    uploaded_by_user=self.user,
                    collection=self.collection,
                    created_at=timezone.now(),
                )
                image.save()
                image.get_file_hash()

        return image


def remove_block_ids(json_object):
    """
    Parse a page JSON representation and strip the block IDs
    """
    if not isinstance(json_object, (dict, list)):
        return json_object
    if isinstance(json_object, list):
        return [remove_block_ids(v) for v in json_object]
    return {k: remove_block_ids(v) for k, v in json_object.items() if k != "id"}
