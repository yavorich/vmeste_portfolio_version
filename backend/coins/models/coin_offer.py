from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Model, PositiveIntegerField

from coins.models import ExchangeRate


class CoinOffer(Model):
    coins = PositiveIntegerField("Количество монет", validators=[MinValueValidator(1)])
    discount = PositiveIntegerField(
        "Скидка, %", default=0, validators=[MaxValueValidator(100)]
    )

    class Meta:
        verbose_name = "Предложение"
        verbose_name_plural = "Предложения о покупке"

    def __str__(self):
        return ""

    @property
    def coins_with_discount(self):
        rate = ExchangeRate.get_solo().rate
        return round(self.coins * (1 - self.discount / 100) * rate)
