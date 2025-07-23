from django.db.models import Model, OneToOneField, CASCADE, IntegerField, CharField


class PaymentInfo(Model):
    user = OneToOneField(
        "api.User",
        on_delete=CASCADE,
        verbose_name="Пользователь",
        related_name="payment_info",
    )

    bank_card_id = IntegerField(blank=True, null=True)
    pan = CharField(max_length=20, blank=True, null=True)
    exp_code = IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Платежная информация"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.email} {self.bank_card_id}"

    @property
    def bank_card_data(self):
        return {"id": self.bank_card_id, "pan": self.pan, "exp_code": self.exp_code}

    def save_bank_card(self, bank_card_info):
        self.bank_card_id = bank_card_info["id"]
        self.pan = bank_card_info["pan"]
        self.exp_code = bank_card_info["exp_code"]
        self.save()

    def reset_bank_card(self):
        self.bank_card_id = None
        self.pan = None
        self.exp_code = None
        self.save()
