# Generated manually for converting attendance field to ArrayField - Step 1: Add new field

from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField


class Migration(migrations.Migration):
    dependencies = [
        ("formations", "0006_alter_formationpage_registration_link"),
    ]

    operations = [
        migrations.AddField(
            model_name="formationpage",
            name="attendance_new",
            field=ArrayField(
                models.CharField(
                    max_length=20,
                    choices=[("enligne", "En ligne"), ("présentiel", "Présentiel"), ("hybride", "Hybride")],
                ),
                size=None,
                blank=True,
                default=list,
                verbose_name="En ligne/Présentiel/Hybride",
            ),
        ),
    ]
