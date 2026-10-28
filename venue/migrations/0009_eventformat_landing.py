from django.db import migrations, models

from venue.landing_content import LANDINGS
from venue.utils import translit_slug


def fill(apps, schema_editor):
    EventFormat = apps.get_model("venue", "EventFormat")
    used = set()
    for obj in EventFormat.objects.order_by("pk"):
        landing = LANDINGS.get(obj.title, {})
        base = landing.get("slug") or translit_slug(obj.title) or f"format-{obj.pk}"
        slug, n = base, 2
        while slug in used:
            slug = f"{base}-{n}"
            n += 1
        used.add(slug)
        obj.slug = slug
        for field in ("landing_h1", "meta_title", "meta_description", "landing_text"):
            if field in landing:
                setattr(obj, field, landing[field])
        obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ("venue", "0008_hall_tonnel_jpg"),
    ]

    operations = [
        migrations.AddField(
            model_name="eventformat",
            name="slug",
            field=models.SlugField(blank=True, max_length=120, null=True, verbose_name="URL"),
        ),
        migrations.AddField(
            model_name="eventformat",
            name="landing_h1",
            field=models.CharField(blank=True, max_length=150, verbose_name="H1 посадочной страницы"),
        ),
        migrations.AddField(
            model_name="eventformat",
            name="meta_title",
            field=models.CharField(blank=True, max_length=70, verbose_name="Meta title"),
        ),
        migrations.AddField(
            model_name="eventformat",
            name="meta_description",
            field=models.CharField(blank=True, max_length=160, verbose_name="Meta description"),
        ),
        migrations.AddField(
            model_name="eventformat",
            name="landing_text",
            field=models.TextField(
                blank=True,
                help_text="Если заполнен — у формата появляется своя страница /events/<url>/. "
                          "Строка, начинающаяся с «## », становится подзаголовком h2",
                verbose_name="Текст посадочной страницы",
            ),
        ),
        migrations.RunPython(fill, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="eventformat",
            name="slug",
            field=models.SlugField(
                blank=True, help_text="Например svadby. Если пусто — сформируется из названия",
                max_length=120, unique=True, verbose_name="URL",
            ),
        ),
    ]
