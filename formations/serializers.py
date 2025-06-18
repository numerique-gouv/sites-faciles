from django.conf import settings
from pyairtable import Api
from rest_framework import serializers
from wagtail_airtable.serializers import AirtableSerializer

from formations.models import Organizer, SubTheme, TargetAudience, Theme


class LowerCharSerializer(serializers.CharField):
    def to_internal_value(self, value):
        return str(value).replace(" ", "").lower()


class TargetAudienceSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        target_audience, _ = TargetAudience.objects.get_or_create(name=data.strip())
        return target_audience

    def get_queryset(self):
        return TargetAudience.objects.all()


class SubThemeSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        sub_theme, _ = SubTheme.objects.get_or_create(name=data.strip())
        return sub_theme

    def get_queryset(self):
        return SubTheme.objects.all()


class ThemeSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        theme_at_id = data.strip()
        try:
            theme_obj = Theme.objects.get(airtable_id=theme_at_id)
        except Theme.DoesNotExist:
            # Theme does not already exist so get infos from airtable
            api = Api(api_key=settings.AIRTABLE_API_KEY)
            at = api.table(
                settings.AIRTABLE_IMPORT_SETTINGS["formations.FormationPage"]["AIRTABLE_BASE_KEY"],
                settings.AIRTABLE_IMPORT_SETTINGS["formations.FormationPage"]["AIRTABLE_TABLE_NAME_THEME"],
            )
            for record in at.all():
                if record["id"] == theme_at_id:
                    at_theme = record
                    break
            theme_obj = Theme.objects.create(airtable_id=theme_at_id, name=at_theme["fields"]["Familles thématiques"])
        return theme_obj

    def get_queryset(self):
        return Theme.objects.all()


class OrganizerSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        organizer_at_id = data.strip()
        try:
            organizer_obj = Organizer.objects.get(airtable_id=organizer_at_id)
        except Organizer.DoesNotExist:
            # Organizer does not already exist so get infos from airtable
            api = Api(api_key=settings.AIRTABLE_API_KEY)
            at = api.table(
                settings.AIRTABLE_IMPORT_SETTINGS["formations.FormationPage"]["AIRTABLE_BASE_KEY"],
                settings.AIRTABLE_IMPORT_SETTINGS["formations.FormationPage"]["AIRTABLE_TABLE_NAME_ORGA"],
            )
            for record in at.all():
                if record["id"] == organizer_at_id:
                    at_organizer = record
                    break
            organizer_obj = Organizer.objects.create(airtable_id=organizer_at_id, name=at_organizer["fields"]["Nom"])
        return organizer_obj

    def get_queryset(self):
        return Organizer.objects.all()


class FormationPageSerializer(AirtableSerializer):
    title = serializers.CharField(max_length=200, required=True)
    name = serializers.CharField(max_length=255, required=True)
    kind = LowerCharSerializer(max_length=20, required=True)
    short_description = serializers.CharField(required=False)
    knowledge_at_the_end = serializers.CharField(required=False)
    duration = serializers.CharField(max_length=255, required=False)
    registration_link = serializers.URLField(required=False)
    target_audience = TargetAudienceSerializer(required=False, many=True)
    themes = ThemeSerializer(required=False, many=True)
    sub_themes = SubThemeSerializer(required=False, many=True)
    organizers = OrganizerSerializer(required=False, many=True)
    image_url = serializers.URLField(required=False)
    visible = serializers.CharField(max_length=3, required=True)
    attendance = LowerCharSerializer(max_length=20, required=True)

    def get_target_audience_list(self, obj):
        return TargetAudienceSerializer(obj.fresh_data, many=True).data

    def get_themes_list(self, obj):
        return ThemeSerializer(obj.fresh_data, many=True).data

    def get_organizers_list(self, obj):
        return OrganizerSerializer(obj.fresh_data, many=True).data
