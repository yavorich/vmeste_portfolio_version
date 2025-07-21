from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.defaults import DECIMAL_PERCENT, DECIMAL_RUB


class Theme(models.Model):
    class PaymentType(models.TextChoices):
        FREE = "FREE", "Бесплатные"
        MASTER = "MASTER", "Платные, платит организатор"
        PROF = "PROF", "Платные, платят участники"

    payment_type = models.CharField(
        "Тип оплаты",
        max_length=16,
        choices=PaymentType.choices,
        default=PaymentType.FREE,
    )

    title = models.CharField(_("Название"), max_length=255, unique=True)
    commission_percent = models.DecimalField(
        "Комиссия сервиса",
        **DECIMAL_PERCENT,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    price = models.DecimalField(
        "Стоимость",
        **DECIMAL_RUB,
        validators=[MinValueValidator(1)],
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title

    @property
    def categories_ordering(self):
        return self.categories.order_by("title")

    def get_commission_percent_factor(self):
        """Множитель для начисления комиссии"""
        assert self.payment_type == self.PaymentType.PROF

        return 1 + self.commission_percent / 100
