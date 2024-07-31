from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db.models import Model, PositiveIntegerField, ManyToManyField, CharField


User = get_user_model()


class PromoCode(Model):
    code = CharField("Код", max_length=16, unique=True)
    coins = PositiveIntegerField("Количество монет", validators=[MinValueValidator(1)])
    quantity = PositiveIntegerField(
        "Количество активаций", validators=[MinValueValidator(1)]
    )
    users_activated = ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    @property
    def user_activated_quantity(self):
        return self.users_activated.count()
