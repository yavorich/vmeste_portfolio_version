from django.db.models import (
    Model,
    TextChoices,
    CharField,
    PositiveIntegerField,
    ForeignKey,
    CASCADE,
    DateTimeField,
)


class WalletHistory(Model):
    class OperationType(TextChoices):
        SPEND = "SPEND", "Расход"
        REFUND = "REFUND", "Возврат"
        REPLENISHMENT = "REPLENISHMENT", "Пополнение"

    operation_type = CharField("Операция", max_length=16, choices=OperationType.choices)
    value = PositiveIntegerField("Количество")
    wallet = ForeignKey(
        "Wallet", on_delete=CASCADE, verbose_name="Кошелек", related_name="history"
    )
    date = DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "операцию"
        verbose_name_plural = "История операций"

    def __str__(self):
        return f"Операция №{self.pk}"
