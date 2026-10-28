"""
Настройки проекта «Подземка» — банкетный зал в стиле лофт / андеграунд.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Для учебного проекта ключ по умолчанию — ок. В бою — только из переменной окружения!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-podzemka-secret-key-change-me-in-production-0123456789",
)

DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = ["127.0.0.1", "localhost", "*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "venue",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "podzemka.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "venue.context_processors.site_info",
            ],
        },
    },
]

WSGI_APPLICATION = "podzemka.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Chita"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Данные о заведении — доступны во всех шаблонах как {{ site.name }}, {{ site.phone }} и т.д.
SITE_INFO = {
    "name": "Подземка",
    "tagline": "Банкетный зал в стиле лофт и андеграунд",
    "legal_name": "ИП Анисимов Игорь Владимирович",
    "domain": "podzemka.example",
    "phone": "+7 (900) 123-45-67",
    "phone_raw": "+79001234567",
    "email": "hello@podzemka.example",
    "address": "улица Курнатовского, 17, Чита, Забайкальский край, 672027",
    "street": "улица Курнатовского, 17",
    "city": "Чита",
    "region": "Забайкальский край",
    "country": "RU",
    "postal_code": "672027",
    "hours": "Ежедневно, 12:00 — 02:00",
    "opens": "12:00",
    "closes": "02:00",
    "price_range": "₽₽",
    "max_guests": 350,
    # Секретная фраза для бара: назвать бармену и получить скидку
    "bar_secret": "Дайте ходу",
    "bar_discount": 14,
    # Координаты строками: так они не превратятся в «52,03553» из-за русской локали
    "geo": {"lat": "52.035530", "lon": "113.493054"},
    "map_url": "https://yandex.ru/maps/?pt=113.493054,52.035530&z=17&l=map",
    "telegram": "https://t.me/podzemka_example",
    "vk": "https://vk.com/podzemka_example",
}

SEO_IDS = {
    "yandex_verification": os.environ.get("YANDEX_VERIFICATION", ""),
    "google_verification": os.environ.get("GOOGLE_SITE_VERIFICATION", ""),
    "metrika_id": os.environ.get("YANDEX_METRIKA_ID", ""),
    "metrika_goal": "booking_sent",
}

# Акция: выпускной + скидка на тамаду. Блок сам исчезает с сайта после даты окончания
# (проверка в venue/context_processors.py).
PROMO = {
    "title": "Выпускной в Подземке",
    "discount": 30,
    "host_name": "Гай Манукян",
    "host_photo": "img/tamada-gai-manukyan.webp",
    "until": "2026-10-01",       # последний день акции (включительно), формат ГГГГ-ММ-ДД
    "until_human": "1 октября",
}
