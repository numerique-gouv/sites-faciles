# Generated by Django 4.2.8 on 2024-01-23 15:57

import django.db.models.deletion
import modelcluster.fields
import wagtail.contrib.forms.models
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("content_manager", "0011_cmsdsfrconfig_search_bar"),
    ]

    operations = [
        migrations.CreateModel(
            name="FormPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "to_address",
                    models.CharField(
                        blank=True,
                        help_text="Optional - form submissions will be emailed to these addresses. Separate multiple addresses by comma.",
                        max_length=255,
                        validators=[wagtail.contrib.forms.models.validate_to_address],
                        verbose_name="to address",
                    ),
                ),
                ("from_address", models.EmailField(blank=True, max_length=255, verbose_name="from address")),
                ("subject", models.CharField(blank=True, max_length=255, verbose_name="subject")),
                ("intro", wagtail.fields.RichTextField(blank=True)),
                ("thank_you_text", wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                "verbose_name": "Page de formulaire",
                "verbose_name_plural": "Pages de formulaire",
            },
            bases=(wagtail.contrib.forms.models.FormMixin, "wagtailcore.page", models.Model),
        ),
        migrations.AlterModelOptions(
            name="contentpage",
            options={"verbose_name": "Page de contenu", "verbose_name_plural": "Pages de contenu"},
        ),
        migrations.CreateModel(
            name="FormField",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sort_order", models.IntegerField(blank=True, editable=False, null=True)),
                (
                    "clean_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Safe name of the form field, the label converted to ascii_snake_case",
                        max_length=255,
                        verbose_name="name",
                    ),
                ),
                (
                    "label",
                    models.CharField(help_text="The label of the form field", max_length=255, verbose_name="label"),
                ),
                (
                    "field_type",
                    models.CharField(
                        choices=[
                            ("singleline", "Single line text"),
                            ("multiline", "Multi-line text"),
                            ("email", "Email"),
                            ("number", "Number"),
                            ("url", "URL"),
                            ("checkbox", "Checkbox"),
                            ("checkboxes", "Checkboxes"),
                            ("dropdown", "Drop down"),
                            ("multiselect", "Multiple select"),
                            ("radio", "Radio buttons"),
                            ("date", "Date"),
                            ("datetime", "Date/time"),
                            ("hidden", "Hidden field"),
                        ],
                        max_length=16,
                        verbose_name="field type",
                    ),
                ),
                ("required", models.BooleanField(default=True, verbose_name="required")),
                (
                    "choices",
                    models.TextField(
                        blank=True,
                        help_text="Comma or new line separated list of choices. Only applicable in checkboxes, radio and dropdown.",
                        verbose_name="choices",
                    ),
                ),
                (
                    "default_value",
                    models.TextField(
                        blank=True,
                        help_text="Default value. Comma or new line separated values supported for checkboxes.",
                        verbose_name="default value",
                    ),
                ),
                ("help_text", models.CharField(blank=True, max_length=255, verbose_name="help text")),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="form_fields",
                        to="content_manager.formpage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]
