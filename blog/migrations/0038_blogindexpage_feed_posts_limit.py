# Generated by Django 5.1.3 on 2024-11-27 10:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0037_alter_blogentrypage_body_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogindexpage",
            name="feed_posts_limit",
            field=models.PositiveSmallIntegerField(
                default=20,
                validators=[
                    django.core.validators.MaxValueValidator(100),
                    django.core.validators.MinValueValidator(1),
                ],
                verbose_name="Post limit in the RSS/Atom feeds",
            ),
        ),
    ]
