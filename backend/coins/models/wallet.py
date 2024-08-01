from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    PositiveIntegerField,
    OneToOneField,
    CASCADE,
    DateField,
)
from django.utils import timezone

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
