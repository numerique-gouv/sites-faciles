import factory
import factory.fuzzy

from content_manager.factories import ContentPageFactory
from formations.enums import Attendance, Kind
from formations.models import FormationPage, Organizer, SubTheme, TargetAudience, Theme


class TargetAudienceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TargetAudience

    name = factory.Faker("sentence", nb_words=3, locale="fr_FR")


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Theme

    name = factory.Faker("sentence", nb_words=3, locale="fr_FR")
    airtable_id = factory.Faker("random_int", min=0, max=10000)


class SubThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubTheme

    name = factory.Faker("sentence", nb_words=3, locale="fr_FR")


class OrganizerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organizer

    name = factory.Faker("sentence", nb_words=3, locale="fr_FR")
    airtable_id = factory.Faker("random_int", min=0, max=10000)


class FormationPageFactory(ContentPageFactory):
    class Meta:
        model = FormationPage

    name = factory.Faker("sentence", nb_words=3, locale="fr_FR")
    kind = factory.fuzzy.FuzzyChoice(Kind.values)
    short_description = factory.Faker("sentence", nb_words=15, locale="fr_FR")
    knowledge_at_the_end = factory.Faker("sentence", nb_words=15, locale="fr_FR")
    duration = factory.Faker("sentence", nb_words=1, locale="fr_FR")
    registration_link = factory.Faker("url")
    image_url = factory.Faker("url")
    attendance = factory.fuzzy.FuzzyChoice(Attendance.values)

    @factory.post_generation
    def target_audience(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for audience in extracted:
                self.target_audience.add(audience)

    @factory.post_generation
    def themes(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for theme in extracted:
                self.themes.add(theme)

    @factory.post_generation
    def organizers(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for organizer in extracted:
                self.organizers.add(organizer)
