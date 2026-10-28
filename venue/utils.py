from django.utils.text import slugify

TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o",
    "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts",
    "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu",
    "я": "ya",
}


def translit_slug(text, max_length=120):
    latin = "".join(TRANSLIT.get(ch, ch) for ch in text.lower())
    return slugify(latin)[:max_length].strip("-")


def unique_slug(instance, text, field="slug"):
    model = type(instance)
    max_length = model._meta.get_field(field).max_length
    base = translit_slug(text, max_length) or model._meta.model_name
    slug, n = base, 2
    while model.objects.filter(**{field: slug}).exclude(pk=instance.pk).exists():
        suffix = f"-{n}"
        slug = base[: max_length - len(suffix)] + suffix
        n += 1
    return slug
