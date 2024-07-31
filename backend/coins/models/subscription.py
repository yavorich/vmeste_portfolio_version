from django.core.validators import MinValueValidator
from django.db.models import Model, PositiveIntegerField, TextChoices, CharField


class CoinSubscription(Model):
    class PeriodType(TextChoices):
        YEAR = "YEAR", "Год"
        MONTH = "MONTH", "Месяц"
        DAY = "DAY", "День"

    quantity = PositiveIntegerField("Количество", validators=[MinValueValidator(1)])
    period_type = CharField("Тип периода", max_length=8, choices=PeriodType.choices)

    price = PositiveIntegerField("Стоимость, Р")
    sort_value = PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ("sort_value",)
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return ""

    @property
    def period_text(self):
        # TODO добавить падежи
        return f"{self.quantity} {self.get_period_type_display().lower()}"
