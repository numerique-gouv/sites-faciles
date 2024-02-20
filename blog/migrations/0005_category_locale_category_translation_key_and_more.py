# Generated by Django 5.0.2 on 2024-02-14 14:04

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0004_blogentrypage_header_image"),
        ("wagtailcore", "0091_remove_revision_submitted_for_moderation"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="locale",
            field=models.ForeignKey(
                default=1,
                editable=False,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="wagtailcore.locale",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="translation_key",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.AlterUniqueTogether(
            name="category",
            unique_together={("name", "locale"), ("slug", "locale"), ("translation_key", "locale")},
        ),
    ]