from django.db import migrations, models

from venue.utils import translit_slug

HALL_SLUGS = {"Депо": "depo", "Тоннель": "tonnel", "Платформа": "platforma", "Вестибюль": "vestibul"}


def fill_slugs(apps, schema_editor):
    for model_name, field, preset in (("Hall", "name", HALL_SLUGS), ("Poster", "title", {})):
        model = apps.get_model("venue", model_name)
        used = set()
        for obj in model.objects.order_by("pk"):
            text = getattr(obj, field)
            base = preset.get(text) or translit_slug(text) or f"{model_name.lower()}-{obj.pk}"
            slug, n = base, 2
            while slug in used:
                slug = f"{base}-{n}"
                n += 1
            used.add(slug)
            obj.slug = slug
            obj.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("venue", "0006_hall_updated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="hall",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, verbose_name="URL"),
        ),
        migrations.AddField(
            model_name="poster",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, verbose_name="URL"),
        ),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="hall",
            name="slug",
            field=models.SlugField(
                blank=True, help_text="Латиницей, например depo. Если пусто — сформируется из названия",
                max_length=120, unique=True, verbose_name="URL",
            ),
        ),
        migrations.AlterField(
            model_name="poster",
            name="slug",
            field=models.SlugField(
                blank=True, help_text="Латиницей. Если пусто — сформируется из названия",
                max_length=120, unique=True, verbose_name="URL",
            ),
        ),
    ]
