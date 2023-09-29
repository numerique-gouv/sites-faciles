from rest_framework import serializers

from wagtail_airtable.serializers import AirtableSerializer
from taggit.models import Tag


class LowerCharSerializer(serializers.CharField):
    def to_internal_value(self, value):
        return str(value).lower()


class TagSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        if type(data) == list:
            print(f"data is a list : {data}")
            tags = []
            for tag in data:
                tag, _ = Tag.objects.get_or_create(name=tag.strip()[:3])
                tags.append(tag)

            print(tags)
            return tags
        return data

    def get_queryset(self):
        return Tag.objects.all()


class FormationPageSerializer(AirtableSerializer):
    title = serializers.CharField(max_length=200, required=True)
    name = serializers.CharField(max_length=255, required=True)
    kind = LowerCharSerializer(max_length=20, required=True)
    short_description = serializers.CharField(required=False)
    knowledge_at_the_end = serializers.CharField(required=False)
    duration = serializers.CharField(max_length=20, required=False)
    registration_link = serializers.URLField(required=False)
    # target_audience = TagSerializer(required=False)
    image_url = serializers.URLField(required=False)
    visible = serializers.CharField(max_length=3, required=True)
