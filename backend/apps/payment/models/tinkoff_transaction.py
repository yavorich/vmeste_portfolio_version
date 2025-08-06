from uuid import uuid4

from django.db.models import (
    Model,
    TextChoices,
    ForeignKey,
    SET_NULL,
    UUIDField,
    CharField,
    URLField,
    DateTimeField,
    IntegerField,
    DecimalField,
)

from apps.api.models import User, Event
from core.defaults import DECIMAL_RUB


class ProductType(TextChoices):
    ORGANIZATION = "organization", "Организация мероприятия"
    PARTICIPANCE = "participance", "Участие в мероприятии"


class TransactionType(TextChoices):
    PAYMENT = "payment", "Основной платёж"
    TRANSFER = "transfer", "Перевод"


class TinkoffTransaction(Model):
    ProductType = ProductType
    TransactionType = TransactionType

    class Status(TextChoices):
        PENDING = "PENDING", "В ожидании"
        MONEY_HOLD = "MONEY_HOLD", "Деньги заморожены"
        SUCCESS = "SUCCESS", "Успешно"
        FAILED = "FAILED", "Неудачно"
        CANCELED = "CANCELED", "Отменено"

    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    event = ForeignKey(Event, on_delete=SET_NULL, null=True)
    product_type = CharField(max_length=20, choices=ProductType.choices, null=True)
    transaction_type = CharField(
        max_length=20, choices=TransactionType.choices, null=True
    )

    price = DecimalField(
        "Сумма к оплате", default=0, help_text="Оплачиваемая сумма в рублях", **DECIMAL_RUB
    )
    deal_id = CharField("Split deal ID", max_length=100, null=True, blank=True)

    uuid = UUIDField("UUID платежа", unique=True, default=uuid4, editable=False)
    payment_id = CharField("Tinkoff payment ID", max_length=100, null=True, blank=True)
    payment_url = URLField("Tinkoff payment url", blank=True, null=True)
    status = CharField(
        "Статус оплаты", max_length=15, choices=Status.choices, default=Status.PENDING
    )
    ticket_id = IntegerField("Номер билета", blank=True, null=True)
    service_reward = DecimalField("Вознаграждение сервиса", default=0, **DECIMAL_RUB)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"

    def __str__(self):
        return str(self.uuid)

    @property
    def product_name(self):
        return self.get_product_type_display()

    @property
    def description(self):
        return self.get_product_type_display()
