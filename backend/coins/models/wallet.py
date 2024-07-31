from django.contrib.auth import get_user_model
from django.db.models import (
    Model,
    PositiveIntegerField,
    OneToOneField,
    BooleanField,
    CASCADE,
)


User = get_user_model()


class Wallet(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    balance = PositiveIntegerField("Баланс", default=10)
    unlimited = BooleanField(
        "Неограниченный",
        default=False,
        help_text="Монеты не будут списываться за операции",
    )

    class Meta:
        verbose_name = "Кошелек"
        verbose_name_plural = "Кошельки"

    def __str__(self):
        return ""
