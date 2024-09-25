import json
import os
from urllib.request import urlretrieve

import requests
from django.conf import settings
from wagtail.images.models import Image

IMAGES_FOLDER = settings.BASE_DIR / "static/template_images"


class ImportExportPage:
    """
    Generic class for import/export of a ContentPage from a wagtail instance
    """

    def __init__(self, source_site, source_page_id) -> None:
        self.source_site = source_site
        self.source_page_id = source_page_id
        self.source_content = self.get_content_from_source_page()

        self.source_body = remove_block_ids(self.source_content["body"])

        self.images = {}
        self.image_ids = []
        self.get_source_images()

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


class ImportExportImage:
    """
    Generic class for import/export of an Image from a wagtail instance
    """

    def __init__(self, source_site, image_ids) -> None:
        self.image_ids = set(image_ids)
        self.source_site = source_site

        # Create the folder for the files if it doesn't exist
        os.makedirs(IMAGES_FOLDER, exist_ok=True)

        self.image_data = self.get_image_data()

    @property
    def image_data_file(self):
        return IMAGES_FOLDER / "image_data.json"

    def get_image_data(self) -> dict:
        if os.path.isfile(self.image_data_file):
            with open(self.image_data_file, "r") as json_file:
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

            image_url = image["meta"]["download_url"]
            image_name = image_url.split("?")[0].split("/")[-1]

            # No need to export the pictograms, as they should already be present
            if "Pictogrammes_DSFR" in image_name:
                pictogram_title = image_name.replace("__", " — ").replace("_", " ")
                pictogram = Image.objects.filter(title=pictogram_title).first()
                self.image_data[i]["local_id"] = pictogram.id
            else:
                urlretrieve(image_url, IMAGES_FOLDER / image_name)

        with open(self.image_data_file, "w") as json_file:
            json.dump(self.image_data, json_file, indent=2)


def remove_block_ids(json_object):
    """
    Parse a page JSON representation and strip the block IDs
    """
    if not isinstance(json_object, (dict, list)):
        return json_object
    if isinstance(json_object, list):
        return [remove_block_ids(v) for v in json_object]
    return {k: remove_block_ids(v) for k, v in json_object.items() if k != "id"}
