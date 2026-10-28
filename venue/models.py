from pathlib import PurePosixPath

from django.contrib.staticfiles import finders
from django.db import models
from django.urls import reverse
from django.utils.formats import date_format

from .utils import unique_slug


DEFAULT_OG_IMAGE = "img/og/default.jpg"


def og_image_for(image):
    if image:
        path = f"img/og/{PurePosixPath(image).stem}.jpg"
        if finders.find(path):
            return path
    return DEFAULT_OG_IMAGE


class Hall(models.Model):
    """Зал (в стилистике сайта — «станция»)."""

    name = models.CharField("Название", max_length=100)

    slug = models.SlugField(
        "URL", max_length=120, unique=True, blank=True,
        help_text="Латиницей, например depo. Если пусто — сформируется из названия",
    )

    line_color = models.CharField(
        "Цвет линии (HEX)", max_length=7, default="#e4312b",
        help_text="Цвет «ветки метро» для зала, например #e4312b",
    )
    line_number = models.PositiveSmallIntegerField("Номер линии", default=1)
    short_description = models.CharField("Короткое описание", max_length=255)
    description = models.TextField("Полное описание")
    capacity_banquet = models.PositiveIntegerField("Вместимость (банкет)")
    capacity_buffet = models.PositiveIntegerField("Вместимость (фуршет)")
    area = models.PositiveIntegerField("Площадь, м²")
    price_from = models.PositiveIntegerField("Цена от, ₽/гость")
    features = models.TextField(
        "Особенности", blank=True,
        help_text="Каждая особенность — с новой строки",
    )
    image = models.CharField(
        "Картинка (путь в static)", max_length=200, default="img/hall-depo.jpg",
    )

    meta_title = models.CharField(
        "Meta title", max_length=70, blank=True,
        help_text="Если пусто — сформируется автоматически",
    )
    meta_description = models.CharField(
        "Meta description", max_length=160, blank=True,
        help_text="Если пусто — сформируется автоматически",
    )

    order = models.PositiveSmallIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать на сайте", default=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("venue:hall_detail", kwargs={"slug": self.slug})

    def features_list(self):
        return [f.strip() for f in self.features.splitlines() if f.strip()]

    def get_meta_title(self):
        if self.meta_title:
            return self.meta_title
        return f"Зал «{self.name}» — банкет до {self.capacity_banquet} гостей в Чите | Подземка"

    def og_image(self):
        return og_image_for(self.image)

    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description
        specs = (
            f"Банкет до {self.capacity_banquet} гостей, фуршет до {self.capacity_buffet}, "
            f"{self.area} м², от {self.price_from} ₽ за гостя."
        )
        text = f"{self.short_description} {specs} Забронируйте онлайн!"
        if len(text) > 160:
            text = f"Лофт-зал «{self.name}» в центре Читы. {specs} Забронируйте онлайн!"
        return text


class EventFormat(models.Model):
    """Формат мероприятия: свадьба, корпоратив, день рождения..."""

    title = models.CharField("Название", max_length=100)
    slug = models.SlugField(
        "URL", max_length=120, unique=True, blank=True,
        help_text="Например svadby. Если пусто — сформируется из названия",
    )
    icon = models.CharField("Иконка (эмодзи или символ)", max_length=8, default="◆")
    description = models.TextField("Описание")
    landing_h1 = models.CharField("H1 посадочной страницы", max_length=150, blank=True)
    meta_title = models.CharField("Meta title", max_length=70, blank=True)
    meta_description = models.CharField("Meta description", max_length=160, blank=True)
    landing_text = models.TextField(
        "Текст посадочной страницы", blank=True,
        help_text="Если заполнен — у формата появляется своя страница /events/<url>/. "
                  "Строка, начинающаяся с «## », становится подзаголовком h2",
    )
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Формат мероприятия"
        verbose_name_plural = "Форматы мероприятий"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def has_landing(self):
        return bool(self.landing_text.strip())

    def get_absolute_url(self):
        return reverse("venue:event_format", kwargs={"slug": self.slug})

    def get_meta_title(self):
        return self.meta_title or f"{self.title} в лофте в Чите | Подземка"

    def get_meta_description(self):
        return self.meta_description or self.description[:160]

    def landing_blocks(self):
        blocks = []
        for chunk in self.landing_text.replace("\r\n", "\n").split("\n\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            if chunk.startswith("## "):
                blocks.append({"type": "h2", "text": chunk[3:].strip()})
            else:
                blocks.append({"type": "p", "text": chunk})
        return blocks


class MenuPackage(models.Model):
    """Банкетный пакет / сет меню."""

    name = models.CharField("Название", max_length=100)
    description = models.CharField("Описание", max_length=255)
    price_per_person = models.PositiveIntegerField("Цена, ₽/гость")
    items = models.TextField("Состав", help_text="Каждая позиция — с новой строки")
    is_featured = models.BooleanField("Хит", default=False)
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Банкетное меню"
        verbose_name_plural = "Банкетные меню"
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def items_list(self):
        return [i.strip() for i in self.items.splitlines() if i.strip()]


class Review(models.Model):
    author = models.CharField("Имя", max_length=100)
    event = models.CharField("Мероприятие", max_length=100, blank=True)
    text = models.TextField("Текст отзыва")
    rating = models.PositiveSmallIntegerField("Оценка (1-5)", default=5)
    created_at = models.DateField("Дата")
    is_published = models.BooleanField("Опубликован", default=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} — {self.rating}★"


class FAQ(models.Model):
    question = models.CharField("Вопрос", max_length=255)
    answer = models.TextField("Ответ")
    order = models.PositiveSmallIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Вопрос-ответ"
        verbose_name_plural = "Вопросы и ответы"
        ordering = ["order", "id"]

    def __str__(self):
        return self.question


class BookingRequest(models.Model):
    """Заявка на бронирование, оставленная через форму на сайте."""

    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_work", "В работе"),
        ("done", "Подтверждена"),
        ("cancel", "Отменена"),
    ]

    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=30)
    date = models.DateField("Дата мероприятия")
    guests = models.PositiveIntegerField("Количество гостей")
    hall = models.ForeignKey(
        Hall, verbose_name="Зал", on_delete=models.SET_NULL, null=True, blank=True,
    )
    event_format = models.ForeignKey(
        EventFormat, verbose_name="Формат", on_delete=models.SET_NULL, null=True, blank=True,
    )
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField("Создана", auto_now_add=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}, {self.date:%d.%m.%Y}, {self.guests} гостей"


class Poster(models.Model):
    """Событие в афише: квиз, концерт, вечеринка — с конкретной датой."""

    title = models.CharField("Название", max_length=150)
    slug = models.SlugField(
        "URL", max_length=120, unique=True, blank=True,
        help_text="Латиницей. Если пусто — сформируется из названия",
    )
    topic = models.CharField("Тема", max_length=150, blank=True)
    organizer = models.CharField("Организатор", max_length=150, blank=True)
    date = models.DateField("Дата", help_text="Для регулярного события — дата первого проведения")
    time = models.TimeField("Время начала", null=True, blank=True)
    schedule = models.CharField(
        "Регулярность", max_length=100, blank=True,
        help_text="Например «Каждое утро». Если заполнено, событие не пропадает из афиши после даты.",
    )
    short_description = models.CharField("Короткое описание", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.CharField("Картинка (путь в static)", max_length=200, blank=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        verbose_name = "Событие афиши"
        verbose_name_plural = "Афиша"
        ordering = ["date", "time"]

    def __str__(self):
        return f"{self.title} ({self.date:%d.%m.%Y})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("venue:poster_detail", kwargs={"slug": self.slug})

    def og_image(self):
        return og_image_for(self.image)

    def when_text(self, with_time=True):
        if self.schedule:
            text = self.schedule.lower()
        else:
            text = date_format(self.date, "j E")
        if with_time and self.time:
            text += f" в {self.time:%H:%M}"
        return text

    def get_meta_title(self):
        for variant in (
            f"{self.title} — {self.when_text()}, Чита | Подземка",
            f"{self.title} — {self.when_text(False)}, Чита | Подземка",
        ):
            if len(variant) <= 65:
                return variant
        return f"{self.title} — {self.when_text(False)} | Подземка"

    def get_meta_description(self):
        text = f"{self.short_description} {self.when_text().capitalize()}, Подземка, Курнатовского, 17. Забронируйте стол!"
        if len(text) > 160:
            text = f"{self.title} в Подземке: {self.when_text()}, Чита, Курнатовского, 17. Подробности и бронирование стола на сайте!"
        return text
