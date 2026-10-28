import datetime

from django.contrib import messages
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
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


def page_meta(name):
    title, description = META[name]
    return {"meta_title": title, "meta_description": description}


def home(request):
    reviews = Review.objects.filter(is_published=True)
    context = {
        "halls": Hall.objects.filter(is_active=True),
        "formats": EventFormat.objects.all()[:6],
        "packages": MenuPackage.objects.filter(is_featured=True)[:3],
        "reviews": reviews[:6],
        "rating": reviews.aggregate(avg=Avg("rating"))["avg"],
        "reviews_count": reviews.count(),
        "faqs": FAQ.objects.all(),
        "posters": upcoming_posters()[:6],
        "form": BookingForm(),
        **page_meta("home"),
    }
    return render(request, "venue/home.html", context)


def hall_list(request):
    return render(request, "venue/hall_list.html", {
        "halls": Hall.objects.filter(is_active=True),
        **page_meta("hall_list"),
    })


def hall_detail(request, pk):
    hall = get_object_or_404(Hall, pk=pk, is_active=True)
    others = Hall.objects.filter(is_active=True).exclude(pk=hall.pk)
    form = BookingForm(initial={"hall": hall})
    return render(request, "venue/hall_detail.html", {
        "hall": hall,
        "others": others,
        "form": form,
        "meta_title": hall.get_meta_title(),
        "meta_description": hall.get_meta_description(),
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
    })


def poster_detail(request, pk):
    # SEO-ВОПРОС: что делать со страницей события, когда оно уже прошло?
    # Отдавать 404? 410? Оставить в архиве с пометкой «событие прошло»?
    poster = get_object_or_404(Poster, pk=pk, is_published=True)
    return render(request, "venue/poster_detail.html", {
        "poster": poster,
        "is_past": not poster.schedule and poster.date < datetime.date.today(),
        "meta_title": poster.get_meta_title(),
        "meta_description": poster.get_meta_description(),
    })


def menu(request):
    return render(request, "venue/menu.html", {
        "packages": MenuPackage.objects.all(),
        **page_meta("menu"),
    })


def events(request):
    return render(request, "venue/events.html", {
        "formats": EventFormat.objects.all(),
        "halls": Hall.objects.filter(is_active=True),
        **page_meta("events"),
    })


def gallery(request):
    # Фото галереи пока лежат в static/img. ПОДСКАЗКА: у картинок нет alt — проверьте шаблон!
    photos = [
        {"src": "img/hall-depo.jpg", "caption": "Зал «Депо»"},
        {"src": "img/hall-tonnel.webp", "caption": "Зал «Тоннель»"},
        {"src": "img/hall-platforma.jpg", "caption": "Зал «Платформа»"},
        {"src": "img/hall-vestibul.jpg", "caption": "Бар «Вестибюль»"},
    ]
    return render(request, "venue/gallery.html", {"photos": photos, **page_meta("gallery")})


def contacts(request):
    return render(request, "venue/contacts.html", page_meta("contacts"))


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
    return render(request, "venue/booking.html", {"form": form, **page_meta("booking")})
