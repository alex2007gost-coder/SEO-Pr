import datetime
import zoneinfo

from django.conf import settings
from django.templatetags.static import static

SCHEMA = "https://schema.org"
WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def postal_address():
    site = settings.SITE_INFO
    return {
        "@type": "PostalAddress",
        "streetAddress": site["street"],
        "addressLocality": site["city"],
        "addressRegion": site["region"],
        "postalCode": site["postal_code"],
        "addressCountry": site["country"],
    }


def venue_id(base_url):
    return f"{base_url}/#venue"


def organization(base_url, reviews=None):
    site = settings.SITE_INFO
    data = {
        "@context": SCHEMA,
        "@type": ["LocalBusiness", "EventVenue"],
        "@id": venue_id(base_url),
        "name": site["name"],
        "legalName": site["legal_name"],
        "description": site["tagline"],
        "url": f"{base_url}/",
        "logo": base_url + static("icons/apple-touch-icon.png"),
        "image": base_url + static("img/og/default.jpg"),
        "telephone": site["phone_raw"],
        "email": site["email"],
        "address": postal_address(),
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": site["geo"]["lat"],
            "longitude": site["geo"]["lon"],
        },
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": WEEK,
            "opens": site["opens"],
            "closes": site["closes"],
        }],
        "hasMap": site["map_url"],
        "sameAs": [site["telegram"], site["vk"]],
        "priceRange": site["price_range"],
        "maximumAttendeeCapacity": site["max_guests"],
    }
    if reviews:
        reviews = list(reviews)
        data["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": round(sum(r.rating for r in reviews) / len(reviews), 1),
            "reviewCount": len(reviews),
            "bestRating": 5,
            "worstRating": 1,
        }
        data["review"] = [{
            "@type": "Review",
            "author": {"@type": "Person", "name": r.author},
            "datePublished": r.created_at.isoformat(),
            "reviewBody": r.text,
            "reviewRating": {"@type": "Rating", "ratingValue": r.rating, "bestRating": 5},
        } for r in reviews]
    return data


def breadcrumb_list(crumbs, base_url, current_path):
    return {
        "@context": SCHEMA,
        "@type": "BreadcrumbList",
        "itemListElement": [{
            "@type": "ListItem",
            "position": i,
            "name": crumb["name"],
            "item": base_url + (crumb["url"] or current_path),
        } for i, crumb in enumerate(crumbs, start=1)],
    }


def faq_page(faqs):
    return {
        "@context": SCHEMA,
        "@type": "FAQPage",
        "mainEntity": [{
            "@type": "Question",
            "name": q.question,
            "acceptedAnswer": {"@type": "Answer", "text": q.answer},
        } for q in faqs],
    }


def local_datetime(date, time):
    tz = zoneinfo.ZoneInfo(settings.TIME_ZONE)
    if time is None:
        return date.isoformat()
    return datetime.datetime.combine(date, time, tzinfo=tz).isoformat()


def repeat_frequency(schedule):
    text = schedule.lower()
    if "недел" in text or "суббот" in text or "пятниц" in text:
        return "P1W"
    if "месяц" in text:
        return "P1M"
    return "P1D"


def event(poster, base_url):
    site = settings.SITE_INFO
    data = {
        "@context": SCHEMA,
        "@type": "Event",
        "name": poster.title,
        "description": poster.short_description,
        "url": base_url + poster.get_absolute_url(),
        "startDate": local_datetime(poster.date, poster.time),
        "eventStatus": f"{SCHEMA}/EventScheduled",
        "eventAttendanceMode": f"{SCHEMA}/OfflineEventAttendanceMode",
        "location": {
            "@type": "Place",
            "@id": venue_id(base_url),
            "name": site["name"],
            "address": postal_address(),
        },
        "organizer": (
            {"@type": "Organization", "name": poster.organizer}
            if poster.organizer
            else {"@type": "Organization", "name": site["name"], "url": f"{base_url}/"}
        ),
    }
    if poster.image:
        data["image"] = [base_url + static(poster.image), base_url + static(poster.og_image())]
    if poster.schedule:
        schedule = {
            "@type": "Schedule",
            "repeatFrequency": repeat_frequency(poster.schedule),
            "startDate": poster.date.isoformat(),
            "scheduleTimezone": settings.TIME_ZONE,
        }
        if poster.time:
            schedule["startTime"] = poster.time.strftime("%H:%M")
        data["eventSchedule"] = schedule
    return data


def menu(packages, base_url):
    return {
        "@context": SCHEMA,
        "@type": "Menu",
        "name": "Банкетное меню Подземки",
        "url": f"{base_url}/menu/",
        "inLanguage": "ru",
        "hasMenuSection": {
            "@type": "MenuSection",
            "name": "Банкетные сеты",
            "hasMenuItem": [{
                "@type": "MenuItem",
                "name": p.name,
                "description": f"{p.description}. Состав: {', '.join(p.items_list())}.",
                "offers": {
                    "@type": "Offer",
                    "price": p.price_per_person,
                    "priceCurrency": "RUB",
                    "description": "Цена за одного гостя",
                },
            } for p in packages],
        },
    }


def promo_offer(promo, base_url):
    return {
        "@context": SCHEMA,
        "@type": "Offer",
        "name": promo["title"],
        "description": f"Скидка {promo['discount']}% на тамаду ({promo['host_name']}) при бронировании выпускного.",
        "url": f"{base_url}/booking/",
        "validThrough": f"{promo['until']}T23:59:59+09:00",
        "image": base_url + static(promo["host_photo"]),
        "offeredBy": {"@id": venue_id(base_url)},
    }
