import json
import uuid

from django.apps import apps as global_apps
from django.db import migrations
from django.db.models import Q, TextField
from django.db.models.functions import Cast
from wagtail.fields import StreamField

# Rows are fetched in small batches: page contents can be large, and loading thousands of
# them at once gets the migration killed on small containers
BATCH_SIZE = 100

# Only rows containing this key can hold a legacy CenteredImageBlock value, which allows
# skipping the other ones in SQL. The legacy keys are still checked in Python.
LEGACY_CENTERED_IMAGE_MARKER = "image_ratio"

# Keys identifying a CenteredImageBlock value saved before its "alt" field was removed
LEGACY_CENTERED_IMAGE_KEYS = {"image", "alt", "width", "image_ratio"}

# The ImageBlock moves the image and its alt text one level down in wagtail-localize paths
LEGACY_TO_IMAGE_BLOCK_PATHS = {"alt": "image.alt_text", "image": "image.image"}

# Same namespace as wagtail_localize.models.TranslationContext._get_path_id
LOCALIZE_PATH_ID_NAMESPACE = uuid.UUID("fcab004a-2b50-11ea-978f-2e728ce88125")


def migrate_centered_image_alt(data):
    """
    Recursively walk raw StreamField data and move the legacy "alt" field of
    CenteredImageBlock values into the alt text of their ImageBlock.
    Returns True if data was modified.
    """
    updated = False

    if isinstance(data, dict):
        if LEGACY_CENTERED_IMAGE_KEYS <= data.keys():
            alt = data.pop("alt") or ""
            image = data["image"]
            if image is None or isinstance(image, int):
                # Always convert, even an empty image: Wagtail can't load a stream mixing
                # image IDs (or None) and ImageBlock values.
                # An empty legacy alt was rendered as alt="", hence decorative.
                data["image"] = {"image": image, "decorative": not alt, "alt_text": alt}
            elif alt and isinstance(image, dict) and not image.get("alt_text"):
                image["alt_text"] = alt
                image["decorative"] = False
            updated = True

        for value in data.values():
            updated = migrate_centered_image_alt(value) or updated

    elif isinstance(data, list):
        for item in data:
            updated = migrate_centered_image_alt(item) or updated

    return updated


def find_legacy_centered_image_paths(data, path):
    """
    Returns the wagtail-localize paths of the legacy CenteredImageBlock values in raw
    StreamField data: stream and list children are identified by their id, struct
    children by their name.
    """
    paths = []

    if isinstance(data, list):
        for item in data:
            paths += find_legacy_centered_image_paths(item, path)

    elif isinstance(data, dict):
        if {"type", "value", "id"} <= data.keys():
            paths += find_legacy_centered_image_paths(data["value"], [*path, data["id"]])
        elif LEGACY_CENTERED_IMAGE_KEYS <= data.keys():
            paths.append(".".join(path))
        else:
            for key, value in data.items():
                paths += find_legacy_centered_image_paths(value, [*path, key])

    return paths


def migrate_pages(apps, schema_editor):
    for model in apps.get_models():
        if model._meta.proxy:
            continue
        stream_fields = [f.name for f in model._meta.get_fields() if isinstance(f, StreamField)]
        if not stream_fields:
            continue

        candidates = Q()
        for field_name in stream_fields:
            candidates |= Q(**{f"legacy_search_{field_name}__contains": LEGACY_CENTERED_IMAGE_MARKER})
        queryset = (
            model.objects.annotate(
                **{f"legacy_search_{field_name}": Cast(field_name, TextField()) for field_name in stream_fields}
            )
            .filter(candidates)
            .only("pk", *stream_fields)
        )

        for instance in queryset.iterator(chunk_size=BATCH_SIZE):
            updated_fields = []
            for field_name in stream_fields:
                raw_data = list(getattr(instance, field_name).raw_data)
                if migrate_centered_image_alt(raw_data):
                    setattr(instance, field_name, raw_data)
                    updated_fields.append(field_name)

            if updated_fields:
                instance.save(update_fields=updated_fields)


def migrate_revisions(apps, schema_editor):
    # Revisions (drafts, scheduled pages...) store StreamFields as JSON strings
    Revision = apps.get_model("wagtailcore", "Revision")

    revisions = (
        Revision.objects.annotate(content_text=Cast("content", TextField()))
        .filter(content_text__contains=LEGACY_CENTERED_IMAGE_MARKER)
        .values_list("pk", "content")
    )

    for pk, content in revisions.iterator(chunk_size=BATCH_SIZE):
        updated = False

        for key, value in content.items():
            if not (isinstance(value, str) and value.startswith("[")):
                continue
            try:
                stream_data = json.loads(value)
            except ValueError:
                continue
            if migrate_centered_image_alt(stream_data):
                content[key] = json.dumps(stream_data)
                updated = True

        if updated:
            Revision.objects.filter(pk=pk).update(content=content)


def migrate_translation_sources(apps, schema_editor):
    # wagtail-localize keeps its own copy of the source content, and identifies each
    # translated value by its path in that content. Both still describe the legacy
    # CenteredImageBlock, which makes publishing a translation fail until the source
    # is synced. Paths are renamed in place so that existing translations are kept.
    try:
        TranslationSource = apps.get_model("wagtail_localize", "TranslationSource")
        TranslationContext = apps.get_model("wagtail_localize", "TranslationContext")
    except LookupError:
        return

    sources = TranslationSource.objects.filter(content_json__contains=LEGACY_CENTERED_IMAGE_MARKER).values_list(
        "pk", "object_id", "content_json"
    )

    for pk, object_id, content_json in sources.iterator(chunk_size=BATCH_SIZE):
        content = json.loads(content_json)
        legacy_paths = []

        for key, value in content.items():
            if not (isinstance(value, str) and value.startswith("[")):
                continue
            try:
                stream_data = json.loads(value)
            except ValueError:
                continue
            legacy_paths += find_legacy_centered_image_paths(stream_data, [key])
            if migrate_centered_image_alt(stream_data):
                content[key] = json.dumps(stream_data)

        if not legacy_paths:
            continue

        TranslationSource.objects.filter(pk=pk).update(content_json=json.dumps(content))

        contexts = TranslationContext.objects.filter(object_id=object_id)
        for path in legacy_paths:
            for legacy_field, new_field in LEGACY_TO_IMAGE_BLOCK_PATHS.items():
                new_path = f"{path}.{new_field}"
                new_path_id = uuid.uuid5(LOCALIZE_PATH_ID_NAMESPACE, new_path)
                if contexts.filter(path_id=new_path_id).exists():
                    continue
                # An empty field_path is recomputed by wagtail-localize when needed
                contexts.filter(path=f"{path}.{legacy_field}").update(
                    path=new_path, path_id=new_path_id, field_path=""
                )


def migrate_all(apps, schema_editor):
    migrate_pages(apps, schema_editor)
    migrate_revisions(apps, schema_editor)
    migrate_translation_sources(apps, schema_editor)


class Migration(migrations.Migration):
    dependencies = [
        ("sites_conformes_core", "0084_alter_catalogindexpage_body_alter_contentpage_body"),
        ("sites_conformes_blog", "0066_alter_blogentrypage_body_alter_blogindexpage_body_and_more"),
        ("sites_conformes_events", "0038_alter_evententrypage_body_alter_eventsindexpage_body"),
        ("wagtailcore", "__latest__"),
    ]
    if global_apps.is_installed("wagtail_localize"):
        dependencies.append(("wagtail_localize", "__latest__"))

    operations = [
        migrations.RunPython(migrate_all, reverse_code=migrations.RunPython.noop),
    ]
