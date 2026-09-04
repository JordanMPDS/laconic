"""Per-account rate limiting.

Two counters, because the minute bucket is checked on every request and the
hour bucket only when the minute bucket is already near its ceiling. Keeping
them separate keeps the hot path to one Redis read.
"""
import time

MINUTE_MAX = 600
HOUR_MAX = 20000


def _minute_key(account, route):
    return "rl:m:%s:%s:%d" % (account, route, int(time.time()) // 60)


def _hour_key(account, route):
    return "rl:h:%s:%s:%d" % (account, route, int(time.time()) // 3600)


def allow(redis, account, route):
    minute = redis.incr(_minute_key(account, route))
    redis.expire(_minute_key(account, route), 120)
    if minute > MINUTE_MAX:
        return False
    if minute < MINUTE_MAX * 0.8:
        return True
    hour = redis.incr(_hour_key(account, route))
    redis.expire(_hour_key(account, route), 7200)
    return hour <= HOUR_MAX


def reconcile(redis, account, day):
    """Fold the hour buckets into the day total, then trim them.

    Runs nightly. The hour buckets expire after two hours, so anything not
    folded here is gone: `quota:day:*` is the only place a whole day's usage
    survives, and it is what billing reads at the end of the month.
    """
    total = 0
    for hour in range(24):
        stamp = day * 86400 // 3600 + hour
        for key in redis.scan_iter("rl:h:%s:*:%d" % (account, stamp)):
            total += int(redis.get(key) or 0)
            redis.delete(key)
    redis.set("quota:day:%s:%d" % (account, day), total)
    return total
