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
