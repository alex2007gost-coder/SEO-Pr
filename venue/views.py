import datetime

from django.contrib import messages
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import BookingForm
from . import schema
from .models import FAQ, EventFormat, Hall, MenuPackage, Poster, Review

META = {
    "home": (
        "Банкетный зал в стиле лофт в Чите на 30–350 гостей | Подземка",
        "Банкетный зал-лофт в Чите на Курнатовского, 17: свадьбы, корпоративы и дни рождения "
        "на 30–350 гостей, своя кухня и бар. Забронируйте дату онлайн!",
    ),
    "hall_list": (
        "Банкетные залы в Чите: 4 лофт-зала от 30 до 350 гостей | Подземка",
        "Четыре банкетных зала в стиле лофт в центре Читы: от камерного «Тоннеля» на 30 гостей "
        "до всей площадки на 350. Сравните залы и выберите свой!",
    ),
    "menu": (
        "Банкетное меню в Чите: сеты и цены на человека | Подземка",
        "Банкетное меню Подземки: сеты от шефа на свадьбу, корпоратив и день рождения, цены "
        "за гостя и калькулятор банкета. Рассчитайте стоимость онлайн!",
    ),
    "events": (
        "Свадьбы, корпоративы и дни рождения в лофте в Чите | Подземка",
        "Проводим свадьбы, корпоративы, выпускные, дни рождения и концерты в лофт-залах "
        "Подземки в Чите — от 20 до 350 гостей. Рассчитайте стоимость!",
    ),
    "poster_list": (
        "Афиша событий в Чите: квизы, концерты и вечеринки | Подземка",
        "Афиша Подземки в Чите: квизы, концерты, кинопоказы, арт-вечеринки и косплей под "
        "кирпичными сводами. Выберите событие и забронируйте стол!",
    ),
    "gallery": (
        "Фото банкетных залов в стиле лофт в Чите — галерея | Подземка",
        "Фотографии банкетных залов Подземки в Чите: кирпичные своды, бетон и неон в залах "
        "«Депо», «Тоннель», «Платформа» и баре. Приходите посмотреть вживую!",
    ),
    "contacts": (
        "Контакты банкетного зала в Чите: Курнатовского, 17 | Подземка",
        "Банкетный зал Подземка в центре Читы: ул. Курнатовского, 17, вход со двора. Телефон "
        "+7 (900) 123-45-67, работаем ежедневно с 12:00 до 02:00. Приезжайте!",
    ),
    "booking": (
        "Бронирование банкетного зала в Чите — онлайн-заявка | Подземка",
        "Оставьте заявку на бронирование банкетного зала Подземка в Чите: подберём зал и меню, "
        "перезвоним в течение 15 минут. Заполните форму онлайн!",
    ),
}


def base_url(request):
    return request.build_absolute_uri("/").rstrip("/")


def breadcrumbs(*items):
    return {"breadcrumbs": [{"name": "Главная", "url": reverse("venue:home")}] + [
        {"name": name, "url": url} for name, url in items
    ]}


def page_meta(name):
    title, description = META[name]
    return {"meta_title": title, "meta_description": description}


def home(request):
    reviews = Review.objects.filter(is_published=True)
    faqs = FAQ.objects.all()
    context = {
        "halls": Hall.objects.filter(is_active=True),
        "formats": EventFormat.objects.all()[:6],
        "packages": MenuPackage.objects.filter(is_featured=True)[:3],
        "reviews": reviews[:6],
        "rating": reviews.aggregate(avg=Avg("rating"))["avg"],
        "reviews_count": reviews.count(),
        "faqs": faqs,
        "schema_reviews": reviews,
        "page_schema": [schema.faq_page(faqs)] if faqs else [],
        "posters": upcoming_posters()[:6],
        "form": BookingForm(),
        **page_meta("home"),
    }
    return render(request, "venue/home.html", context)


def hall_list(request):
    return render(request, "venue/hall_list.html", {
        "halls": Hall.objects.filter(is_active=True),
        **page_meta("hall_list"),
        **breadcrumbs(("Залы", None)),
    })


def hall_redirect(request, pk):
    hall = get_object_or_404(Hall, pk=pk, is_active=True)
    return redirect(hall, permanent=True)


def hall_detail(request, slug):
    hall = get_object_or_404(Hall, slug=slug, is_active=True)
    others = Hall.objects.filter(is_active=True).exclude(pk=hall.pk)
    form = BookingForm(initial={"hall": hall})
    return render(request, "venue/hall_detail.html", {
        "hall": hall,
        "others": others,
        "form": form,
        "meta_title": hall.get_meta_title(),
        "meta_description": hall.get_meta_description(),
        "og_image": hall.og_image(),
        "og_image_alt": f"Банкетный зал «{hall.name}» в Подземке",
        **breadcrumbs(("Залы", reverse("venue:hall_list")), (hall.name, None)),
    })


def upcoming_posters():
    """Будущие события + регулярные (у них заполнено поле schedule)."""
    return Poster.objects.filter(is_published=True).filter(
        Q(date__gte=datetime.date.today()) | ~Q(schedule=""),
    )


def poster_list(request):
    return render(request, "venue/poster_list.html", {
        "posters": upcoming_posters(),
        **page_meta("poster_list"),
        **breadcrumbs(("Афиша", None)),
    })


def poster_redirect(request, pk):
    poster = get_object_or_404(Poster, pk=pk, is_published=True)
    return redirect(poster, permanent=True)


def poster_detail(request, slug):
    poster = get_object_or_404(Poster, slug=slug, is_published=True)
    return render(request, "venue/poster_detail.html", {
        "poster": poster,
        "is_past": not poster.schedule and poster.date < datetime.date.today(),
        "meta_title": poster.get_meta_title(),
        "meta_description": poster.get_meta_description(),
        "og_image": poster.og_image(),
        "og_image_alt": poster.title,
        "page_schema": [schema.event(poster, base_url(request))],
        **breadcrumbs(("Афиша", reverse("venue:poster_list")), (poster.title, None)),
    })


def menu(request):
    packages = MenuPackage.objects.all()
    return render(request, "venue/menu.html", {
        "packages": packages,
        "page_schema": [schema.menu(packages, base_url(request))] if packages else [],
        **page_meta("menu"),
        **breadcrumbs(("Банкетное меню", None)),
    })


def events(request):
    return render(request, "venue/events.html", {
        "formats": EventFormat.objects.all(),
        "halls": Hall.objects.filter(is_active=True),
        **page_meta("events"),
        **breadcrumbs(("Мероприятия", None)),
    })


def gallery(request):
    photos = [
        {"src": "img/hall-depo.jpg", "caption": "Зал «Депо»",
         "alt": "Банкетный зал «Депо»: кирпичные своды, сцена и световая ферма"},
        {"src": "img/hall-tonnel.webp", "caption": "Зал «Тоннель»",
         "alt": "Камерный зал «Тоннель» с арочным бетонным потолком и неоновой подсветкой"},
        {"src": "img/hall-platforma.jpg", "caption": "Зал «Платформа»",
         "alt": "Зал «Платформа» — большое лофт-пространство с танцполом и баром"},
        {"src": "img/hall-vestibul.jpg", "caption": "Бар «Вестибюль»",
         "alt": "Бар «Вестибюль» с бетонной барной стойкой и лаунж-зоной"},
    ]
    return render(request, "venue/gallery.html", {
        "photos": photos, **page_meta("gallery"), **breadcrumbs(("Галерея", None)),
    })


def contacts(request):
    return render(request, "venue/contacts.html", {
        **page_meta("contacts"), **breadcrumbs(("Контакты", None)),
    })


def booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Заявка принята! Перезвоним в течение 15 минут.")
            return redirect("venue:booking")
    else:
        form = BookingForm(initial={
            "hall": request.GET.get("hall"),
            "comment": request.GET.get("comment", ""),
            "guests": request.GET.get("guests"),
        })
    return render(request, "venue/booking.html", {
        "form": form, **page_meta("booking"), **breadcrumbs(("Бронирование", None)),
    })


def page_not_found(request, exception=None):
    return render(request, "404.html", {
        "meta_title": "Страница не найдена (404) | Подземка",
        "meta_description": "Такой страницы в Подземке нет. Перейдите на главную, выберите банкетный зал или посмотрите афишу событий.",
        "hide_canonical": True,
        "halls": Hall.objects.filter(is_active=True),
    }, status=404)
