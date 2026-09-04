"""Monthly invoice lines, built from the day totals reconcile() writes."""


def month_usage(redis, account, days):
    return sum(int(redis.get("quota:day:%s:%d" % (account, d)) or 0)
               for d in days)
