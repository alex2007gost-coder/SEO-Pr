from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from venue.sitemaps import EventFormatSitemap, HallSitemap, PosterSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "halls": HallSitemap,
    "events": EventFormatSitemap,
    "afisha": PosterSitemap,
}

urlpatterns = [
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain; charset=utf-8")),
    path("favicon.ico", RedirectView.as_view(url=static("icons/favicon.ico"), permanent=True)),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("admin/", admin.site.urls),
    path("", include("venue.urls")),
]

handler404 = "venue.views.page_not_found"
