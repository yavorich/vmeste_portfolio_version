from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import (
    Model,
    PositiveIntegerField,
    ManyToManyField,
    CharField,
    Manager,
    Count,
    F,
)

User = get_user_model()


class PromoCodeManager(Manager):
    def active_list(self):
        return self.annotate(_user_activated_quantity=Count("users_activated")).filter(
            _user_activated_quantity__lt=F("quantity")
        )


class PromoCode(Model):
    code = CharField("Код", max_length=16, unique=True)
    coins = PositiveIntegerField("Количество монет", validators=[MinValueValidator(1)])
    quantity = PositiveIntegerField(
        "Количество активаций", validators=[MinValueValidator(1)]
    )
    users_activated = ManyToManyField(User, blank=True)

    objects = PromoCodeManager()

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    @property
    def user_activated_quantity(self):
        return self.users_activated.count()

    def activate(self, user: User):
        self.users_activated.add(user)
        self.save()
        user.wallet.balance += self.coins
        user.wallet.save()
