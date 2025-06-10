from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    Model,
    OneToOneField,
    CASCADE,
    CharField,
    TextField,
    DateTimeField,
    URLField,
    BooleanField,
)
from phonenumber_field.modelfields import PhoneNumberField

from apps.api.validators import validate_only_digits
from apps.api.models.user import User


class LegalEntity(Model):
    user = OneToOneField(User, on_delete=CASCADE, related_name="legal_entity")

    company_name = CharField("Название компании", max_length=256)

    legal_address = TextField("Юридический адрес")

    full_name = CharField("ФИО ответственного")
    phone_number = PhoneNumberField("Номер телефона ответственного")

    director_full_name = CharField("ФИО директора")
    director_phone_number = PhoneNumberField("Номер телефона директора")

    inn = CharField("ИНН", max_length=12, validators=[validate_only_digits])
    # kpp = CharField("КПП", max_length=9, validators=[validate_only_digits])
    ogrn = CharField("ОГРН", max_length=13, validators=[validate_only_digits])
    # okved = CharField("ОКВЭД", max_length=11)
    bic = CharField("БИК банка", max_length=9, validators=[validate_only_digits])
    bank_name = CharField("Название банка", max_length=256)
    current_account = CharField(
        "Номер расчетного счета в рублях",
        max_length=20,
        validators=[validate_only_digits],
    )

    sites = ArrayField(URLField(), default=list)

    confirmed = BooleanField("Подтверждён", default=False)

    created_at = DateTimeField("Дата регистрации", auto_now_add=True)

    class Meta:
        verbose_name = "Карточка юр. лица"
        verbose_name_plural = "Карточки юр. лица"

    def __str__(self):
        return self.company_name
