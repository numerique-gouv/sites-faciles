import requests


class ImportExportPage:
    """
    Generic class for data import/export a ContentPage from a wagtail instance
    """

    def __init__(self, source_site, source_page_id) -> None:
        self.source_site = source_site
        self.source_page_id = source_page_id
        self.source_content = self.get_content_from_source()

        self.source_body = remove_block_ids(self.source_content["body"])

        self.images = {}
        self.image_ids = []
        self.get_source_images()

    @property
    def source_page_api_url(self):
        return f"{self.source_site}api/v2/pages/{self.source_page_id}/"

    def get_content_from_source(self):
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


def remove_block_ids(json_object):
    """
    Parse a page JSON representation and strip the block IDs
    """
    if not isinstance(json_object, (dict, list)):
        return json_object
    if isinstance(json_object, list):
        return [remove_block_ids(v) for v in json_object]
    return {k: remove_block_ids(v) for k, v in json_object.items() if k != "id"}
