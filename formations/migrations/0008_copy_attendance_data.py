# Generated manually for converting attendance field to ArrayField - Step 2: Copy data

from django.db import migrations


def copy_attendance_data(apps, schema_editor):
    """
    Copy attendance data from old field to new field as arrays
    """
    FormationPage = apps.get_model("formations", "FormationPage")

    for formation in FormationPage.objects.all():
        if formation.attendance:
            formation.attendance_new = [formation.attendance]
            formation.save(update_fields=["attendance_new"])


def reverse_copy_attendance_data(apps, schema_editor):
    """
    Copy attendance data back from new field to old field
    """
    FormationPage = apps.get_model("formations", "FormationPage")

    for formation in FormationPage.objects.all():
        if formation.attendance_new and len(formation.attendance_new) > 0:
            formation.attendance = formation.attendance_new[0]
            formation.save(update_fields=["attendance"])


class Migration(migrations.Migration):
    dependencies = [
        ("formations", "0007_add_attendance_new_field"),
    ]

    operations = [
        migrations.RunPython(
            copy_attendance_data,
            reverse_copy_attendance_data,
        ),
    ]
