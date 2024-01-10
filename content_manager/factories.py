import factory
from wagtail.models import Page

from content_manager.models import ContentPage


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    # override the _create method, to establish parent-child relationship between page and home
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = Page.objects.filter(slug="home").first()
        page = model_class(*args, **kwargs)
        parent.add_child(instance=page)
        return page


class ContentPageFactory(PageFactory):
    """Generates ContentPage() objects for unit tests."""

    class Meta:
        model = ContentPage

    class Params:
        with_seo_title = factory.Trait(
            seo_title=factory.Faker("sentence", nb_words=5, variable_nb_words=True, locale="fr_FR")
        )
        with_search_description = factory.Trait(
            search_description=factory.Faker("sentence", nb_words=10, variable_nb_words=True, locale="fr_FR")
        )

    slug = factory.Faker("slug")
    title = factory.Faker("sentence", nb_words=5, locale="fr_FR")
