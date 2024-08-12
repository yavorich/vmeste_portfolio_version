from django.core.validators import MinValueValidator
from django.db.models import Model, PositiveIntegerField, TextChoices, CharField
from django.utils import timezone

from .product import ProductMixin


class CoinSubscription(ProductMixin, Model):
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

    @property
    def name(self):
        return f"Подписка на {self.period_type}"

    description = "Подписка на безлимитные монеты"

    def buy(self, user):
        today = timezone.now().date()
        if user.wallet.unlimited_until is not None:  # если подписка уже активирована
            today = max(user.wallet.unlimited_until, today)

        match self.period_type:
            case self.PeriodType.YEAR:
                unlimited_until = today.replace(year=today.year + self.quantity)
            case self.PeriodType.MONTH:
                months = today.month + self.quantity
                year = today.year + months // 12
                month = months % 12
                unlimited_until = today.replace(year=year, month=month)
            case self.PeriodType.DAY:
                unlimited_until = today + timezone.timedelta(days=self.quantity)
            case _:
                raise NotImplementedError

        user.wallet.unlimited_until = unlimited_until
        user.wallet.save()
