from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Hall
from .views import upcoming_posters


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"

    PAGES = {
        "venue:home": 1.0,
        "venue:hall_list": 0.9,
        "venue:events": 0.8,
        "venue:menu": 0.8,
        "venue:poster_list": 0.7,
        "venue:gallery": 0.6,
        "venue:contacts": 0.7,
    }

    def items(self):
        return list(self.PAGES)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PAGES[item]


class HallSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Hall.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class PosterSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return upcoming_posters()
