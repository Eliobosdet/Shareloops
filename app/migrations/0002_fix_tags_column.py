from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),  # Sostituisci con l'ultima migrazione
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE app_samplepack ADD COLUMN tags VARCHAR(255);",
            "ALTER TABLE app_samplepack DROP COLUMN tags;"
        )
    ]