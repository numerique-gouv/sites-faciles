# Generated by Django 5.1.7 on 2025-04-01 14:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("forms", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="formfield",
            options={"ordering": ["sort_order"], "verbose_name": "Form field", "verbose_name_plural": "Form fields"},
        ),
    ]
