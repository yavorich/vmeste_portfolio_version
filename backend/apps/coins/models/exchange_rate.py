from solo.models import SingletonModel
from django.db.models import PositiveIntegerField


class ExchangeRate(SingletonModel):
    rate = PositiveIntegerField("1*, рублей", default=100)

    class Meta:
        verbose_name = "Номинал"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self._meta.verbose_name
