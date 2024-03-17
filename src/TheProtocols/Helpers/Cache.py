cache = []


def get_cached_object(type, identifier: str, value):
    for i in cache:
        if isinstance(i, type) and getattr(i, identifier) == value:
            return i


def add_to_cache(obj):
    cache.append(obj)
