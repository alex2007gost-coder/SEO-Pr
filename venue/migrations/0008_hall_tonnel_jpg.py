from django.db import migrations


def forwards(apps, schema_editor):
    Hall = apps.get_model("venue", "Hall")
    Hall.objects.filter(image="img/hall-tonnel.webp").update(image="img/hall-tonnel.jpg")


def backwards(apps, schema_editor):
    Hall = apps.get_model("venue", "Hall")
    Hall.objects.filter(image="img/hall-tonnel.jpg").update(image="img/hall-tonnel.webp")


class Migration(migrations.Migration):

    dependencies = [
        ("venue", "0007_slugs"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
