import json

from django import template
from django.utils.safestring import mark_safe

from .. import schema

register = template.Library()

ESCAPES = {ord("<"): "\\u003c", ord(">"): "\\u003e", ord("&"): "\\u0026"}


def render(data):
    if not data:
        return ""
    payload = json.dumps(data, ensure_ascii=False, indent=2).translate(ESCAPES)
    return mark_safe(f'<script type="application/ld+json">\n{payload}\n</script>')


@register.simple_tag
def jsonld(data):
    return render(data)


@register.simple_tag(takes_context=True)
def organization_jsonld(context):
    return render(schema.organization(context["base_url"], context.get("schema_reviews")))


@register.simple_tag(takes_context=True)
def breadcrumbs_jsonld(context):
    crumbs = context.get("breadcrumbs")
    if not crumbs:
        return ""
    return render(schema.breadcrumb_list(crumbs, context["base_url"], context["request"].path))


@register.simple_tag(takes_context=True)
def promo_jsonld(context):
    promo = context.get("promo")
    return render(schema.promo_offer(promo, context["base_url"])) if promo else ""
