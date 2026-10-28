from functools import lru_cache

from django import template
from django.contrib.staticfiles import finders
from django.utils.html import format_html

register = template.Library()


@lru_cache(maxsize=256)
def static_image_size(path):
    from PIL import Image

    found = finders.find(path)
    if not found:
        return None
    with Image.open(found) as im:
        return im.size


@register.simple_tag
def img_size(path):
    size = static_image_size(path) if path else None
    if not size:
        return ""
    return format_html('width="{}" height="{}"', *size)


def variant(path, suffix, ext):
    stem, _, _ = path.rpartition(".")
    candidate = f"{stem}{suffix}.{ext}"
    return candidate if finders.find(candidate) else None


@register.inclusion_tag("includes/picture.html")
def picture(path, alt, sizes="100vw", lazy=False, priority=False):
    sources = []
    for ext, mime in (("webp", "image/webp"), ("jpg", "image/jpeg")):
        items = []
        for suffix in ("-600", ""):
            found = variant(path, suffix, ext)
            if found:
                size = static_image_size(found)
                items.append((found, size[0]))
        if items:
            sources.append({"type": mime, "items": items})
    size = static_image_size(path) or (None, None)
    return {
        "src": path, "alt": alt, "sizes": sizes, "lazy": lazy, "priority": priority,
        "width": size[0], "height": size[1],
        "webp": next((s for s in sources if s["type"] == "image/webp"), None),
        "jpeg": next((s for s in sources if s["type"] == "image/jpeg"), None),
    }


@register.filter
def gt(value, arg):
    return value > arg
