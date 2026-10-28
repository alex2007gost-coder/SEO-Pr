import datetime

from django.conf import settings

from .models import Hall


def site_info(request):
    """Общие данные для всех шаблонов: контакты, список залов для меню и текущая акция."""
    promo = settings.PROMO
    promo_active = datetime.date.today() <= datetime.date.fromisoformat(promo["until"])
    return {
        "site": settings.SITE_INFO,
        "seo_ids": settings.SEO_IDS,
        "base_url": request.build_absolute_uri("/").rstrip("/"),
        "nav_halls": Hall.objects.filter(is_active=True),
        "promo": promo if promo_active else None,
    }
