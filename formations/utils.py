from content_manager.models import ContentPage


def get_parent_page_of_formation_page():
    page = ContentPage.objects.get(slug="catalogue")
    return page.pk
