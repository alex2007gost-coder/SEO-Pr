"""
Автотесты сайта. Запуск: python manage.py test
"""

import datetime
import io
import json
import re
from unittest import mock

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import BookingRequest, EventFormat, Hall, Poster


class SiteTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", stdout=io.StringIO())


class PagesTest(SiteTestCase):
    def test_static_pages_ok(self):
        for name in ["home", "hall_list", "menu", "events", "gallery", "contacts", "booking", "poster_list"]:
            with self.subTest(page=name):
                self.assertEqual(self.client.get(reverse(f"venue:{name}")).status_code, 200)

    def test_every_hall_and_poster_page_ok(self):
        for obj in [*Hall.objects.all(), *Poster.objects.all()]:
            with self.subTest(url=obj.get_absolute_url()):
                self.assertEqual(self.client.get(obj.get_absolute_url()).status_code, 200)

    def test_inactive_hall_is_404(self):
        hall = Hall.objects.first()
        hall.is_active = False
        hall.save()
        self.assertEqual(self.client.get(hall.get_absolute_url()).status_code, 404)

    def test_admin_login_works(self):
        self.assertTrue(self.client.login(username="admin", password="podzemka2026"))


class BookingTest(SiteTestCase):
    def form_data(self, **overrides):
        data = {
            "name": "Тест", "phone": "+7 (900) 000-00-00",
            "date": (datetime.date.today() + datetime.timedelta(days=30)).isoformat(),
            "guests": 50, "hall": Hall.objects.first().pk,
        }
        data.update(overrides)
        return data

    def test_booking_is_saved(self):
        response = self.client.post(reverse("venue:booking"), self.form_data(), follow=True)
        self.assertEqual(BookingRequest.objects.count(), 1)
        self.assertContains(response, "Заявка принята")

    def test_past_date_is_rejected(self):
        self.client.post(reverse("venue:booking"), self.form_data(date="2020-01-01"))
        self.assertEqual(BookingRequest.objects.count(), 0)

    def test_calculator_prefills_form(self):
        response = self.client.get(reverse("venue:booking"), {"guests": 120, "comment": "Расчёт с сайта"})
        self.assertContains(response, 'value="120"')
        self.assertContains(response, "Расчёт с сайта")


class PromoAndPosterTest(SiteTestCase):
    def test_promo_hidden_after_deadline(self):
        with mock.patch("venue.context_processors.datetime") as dt:
            dt.date.today.return_value = datetime.date(2099, 1, 1)
            dt.date.fromisoformat = datetime.date.fromisoformat
            response = self.client.get(reverse("venue:home"))
        self.assertIsNone(response.context["promo"])

    def test_past_poster_not_listed_but_regular_is(self):
        past = Poster.objects.create(
            title="Прошедшее", date=datetime.date(2020, 1, 1), short_description="-",
        )
        regular = Poster.objects.create(
            title="Регулярное", date=datetime.date(2020, 1, 1), schedule="Каждый день", short_description="-",
        )
        posters = list(self.client.get(reverse("venue:poster_list")).context["posters"])
        self.assertNotIn(past, posters)
        self.assertIn(regular, posters)


class SeoTest(SiteTestCase):
    def public_urls(self):
        names = ["home", "hall_list", "menu", "events", "gallery", "contacts", "poster_list"]
        urls = [reverse(f"venue:{n}") for n in names]
        urls += [h.get_absolute_url() for h in Hall.objects.filter(is_active=True)]
        urls += [p.get_absolute_url() for p in Poster.objects.all()]
        urls += [f.get_absolute_url() for f in EventFormat.objects.all() if f.has_landing()]
        return urls

    def html(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return response.content.decode()

    def test_lang_attribute(self):
        self.assertIn('<html lang="ru">', self.html("/"))

    def test_unique_titles_and_descriptions(self):
        titles, descriptions = {}, {}
        for url in self.public_urls():
            html = self.html(url)
            title = re.search(r"<title>(.*?)</title>", html).group(1)
            description = re.search(r'<meta name="description" content="(.*?)">', html).group(1)
            with self.subTest(url=url):
                self.assertNotIn(title, titles, f"title повторяется с {titles.get(title)}")
                self.assertNotIn(description, descriptions)
                self.assertLessEqual(len(description), 160)
                self.assertGreaterEqual(len(description), 100)
            titles[title], descriptions[description] = url, url

    def test_canonical_and_og_absolute(self):
        for url in self.public_urls():
            html = self.html(url)
            with self.subTest(url=url):
                self.assertIn(f'<link rel="canonical" href="http://testserver{url}">', html)
                self.assertRegex(html, r'<meta property="og:image" content="http://testserver/static/[^"]+\.jpg">')
                self.assertIn('<meta name="twitter:card" content="summary_large_image">', html)

    def test_hall_og_image_is_hall_photo(self):
        hall = Hall.objects.get(slug="depo")
        self.assertIn("/static/img/og/hall-depo.jpg", self.html(hall.get_absolute_url()))

    def test_exactly_one_h1(self):
        for url in self.public_urls() + [reverse("venue:booking")]:
            with self.subTest(url=url):
                self.assertEqual(len(re.findall(r"<h1[\s>]", self.html(url))), 1)

    def test_no_heading_level_skips(self):
        for url in self.public_urls():
            levels = [int(x) for x in re.findall(r"<h([1-6])[\s>]", self.html(url))]
            with self.subTest(url=url):
                for prev, cur in zip(levels, levels[1:]):
                    self.assertLessEqual(cur - prev, 1)

    def test_all_images_have_alt_and_size(self):
        for url in self.public_urls():
            for img in re.findall(r"<img[^>]*>", self.html(url)):
                with self.subTest(url=url, img=img):
                    self.assertRegex(img, r'alt="[^"]+"')
                    self.assertIn("width=", img)
                    self.assertIn("height=", img)

    def test_booking_noindex(self):
        self.assertIn('<meta name="robots" content="noindex, follow">', self.html(reverse("venue:booking")))

    def test_robots_txt(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        text = response.content.decode()
        self.assertIn("Sitemap: http://testserver/sitemap.xml", text)
        self.assertIn("Disallow: /admin/", text)

    def test_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        xml = response.content.decode()
        self.assertNotIn("/booking/", xml)
        self.assertNotIn("/home/", xml)
        self.assertIn("http://testserver/halls/depo/", xml)
        self.assertIn("<lastmod>", xml)
        self.assertIn("/events/svadby/", xml)

    def test_redirects(self):
        hall = Hall.objects.get(slug="depo")
        poster = Poster.objects.first()
        cases = {
            "/home/": "/",
            f"/halls/{hall.pk}/": "/halls/depo/",
            f"/afisha/{poster.pk}/": poster.get_absolute_url(),
        }
        for old, new in cases.items():
            with self.subTest(url=old):
                response = self.client.get(old)
                self.assertEqual(response.status_code, 301)
                self.assertEqual(response["Location"], new)

    def test_slug_urls(self):
        self.assertEqual(Hall.objects.get(name="Тоннель").get_absolute_url(), "/halls/tonnel/")
        self.assertEqual(Poster.objects.get(title="Квиз «60 секунд»").get_absolute_url(), "/afisha/kviz-60-sekund/")

    @override_settings(DEBUG=False)
    def test_custom_404(self):
        response = self.client.get("/net-takoy-stranicy/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Станция не найдена", status_code=404)
        self.assertContains(response, 'content="noindex, follow"', status_code=404)

    def jsonld_types(self, url):
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html(url), re.S)
        types = []
        for block in blocks:
            t = json.loads(block)["@type"]
            types += t if isinstance(t, list) else [t]
        return types

    def test_jsonld(self):
        self.assertIn("EventVenue", self.jsonld_types("/"))
        self.assertIn("FAQPage", self.jsonld_types("/"))
        self.assertIn("BreadcrumbList", self.jsonld_types("/halls/depo/"))
        self.assertIn("Event", self.jsonld_types(Poster.objects.first().get_absolute_url()))
        self.assertIn("Menu", self.jsonld_types(reverse("venue:menu")))

    def test_regular_event_has_schedule(self):
        poster = Poster.objects.exclude(schedule="").first()
        html = self.html(poster.get_absolute_url())
        self.assertIn('"eventSchedule"', html)
        self.assertIn("+09:00", html)

    def test_landing_pages(self):
        for slug in ("svadby", "korporativy"):
            fmt = EventFormat.objects.get(slug=slug)
            text = re.sub(r"^## .*$", "", fmt.landing_text, flags=re.M)
            with self.subTest(slug=slug):
                self.assertGreaterEqual(len(text), 1500)
                self.assertEqual(self.client.get(f"/events/{slug}/").status_code, 200)
