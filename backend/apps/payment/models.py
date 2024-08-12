from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    TextChoices,
    ForeignKey,
    SET_NULL,
    UUIDField,
    CharField,
    URLField,
    PositiveIntegerField,
    DateTimeField,
)


User = get_user_model()


class ProductType(TextChoices):
    COINS = "coins", "Монеты"
    SUBSCRIPTION = "subscription", "Подписка"


class TinkoffTransaction(Model):
    ProductType = ProductType

    class Status(TextChoices):
        PENDING = "PENDING", "В ожидании"
        MONEY_HOLD = "MONEY_HOLD", "Деньги заморожены"
        SUCCESS = "SUCCESS", "Успешно"
        FAILED = "FAILED", "Неудачно"
        CANCELED = "CANCELED", "Отменено"

    user = ForeignKey(User, on_delete=SET_NULL, null=True)

    product_type = CharField(
        "Тип продукта",
        max_length=16,
        choices=ProductType.choices,
    )
    product_id = PositiveIntegerField()
    price = PositiveIntegerField(
        "Сумма к оплате",
        default=0,
        help_text="Оплачиваемая сумма в рублях",
    )

    uuid = UUIDField("UUID платежа", unique=True, default=uuid4, editable=False)
    payment_id = CharField(
        "Tinkoff payment ID",
        max_length=100,
        null=True,
        blank=True,
    )
    payment_url = URLField("Tinkoff payment url", blank=True, null=True)
    status = CharField(
        "Статус оплаты",
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return self.uuid
