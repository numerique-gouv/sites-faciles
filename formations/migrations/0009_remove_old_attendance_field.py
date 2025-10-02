# Generated manually for converting attendance field to ArrayField - Step 3: Remove old field and rename

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("formations", "0008_copy_attendance_data"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="formationpage",
            name="attendance",
        ),
        migrations.RenameField(
            model_name="formationpage",
            old_name="attendance_new",
            new_name="attendance",
        ),
    ]
