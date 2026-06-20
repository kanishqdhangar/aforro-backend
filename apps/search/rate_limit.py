from django.core.cache import cache


def is_rate_limited(ip_address):

    key = f"rate_limit:{ip_address}"

    current = cache.get(key, 0)

    if current >= 20:
        return True

    if current == 0:
        cache.set(
            key,
            1,
            timeout=60
        )
    else:
        cache.incr(key)

    return False