from django.template.defaultfilters import date as _date
from django.utils.timezone import localtime, datetime


def humanize_date(date: str):
    date = datetime.strptime(date, "%Y-%m-%d").date()
    delta = date - localtime().date()
    names = ["Сегодня", "Завтра", "Послезавтра"]
    if delta.days < len(names):
        return names[delta.days]
    if delta.days <= 6:
        return _date(date, "l")
    return "Позже"
