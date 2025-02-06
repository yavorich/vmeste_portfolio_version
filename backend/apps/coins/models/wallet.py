from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    PositiveIntegerField,
    OneToOneField,
    CASCADE,
    DateField,
)
from django.utils import timezone

from .history import WalletHistory

User = get_user_model()


class Wallet(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    balance = PositiveIntegerField("Баланс", default=10)
    unlimited_until = DateField(
        "Неограниченный до даты",
        null=True,
        blank=True,
        help_text="Монеты не будут списываться за операции до установленной даты",
    )

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"

    def __str__(self):
        return ""

    @property
    def unlimited(self):
        return (
            self.unlimited_until is not None
            and timezone.now().date() <= self.unlimited_until
        )

    def has_coin(self, coins: int) -> bool:
        return self.unlimited or coins <= self.balance

    def spend(self, coins: int):
        if not self.unlimited:
            self.balance -= coins
            self.save()
            WalletHistory.objects.create(
                operation_type=WalletHistory.OperationType.SPEND,
                value=coins,
                wallet=self,
            )

    def refund(self, coins: int):
        if not self.unlimited:
            self.balance += coins
            self.save()
            WalletHistory.objects.create(
                operation_type=WalletHistory.OperationType.REFUND,
                value=coins,
                wallet=self,
            )
