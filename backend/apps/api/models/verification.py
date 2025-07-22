from django.db.models import Model, OneToOneField, CASCADE, FileField, BooleanField

from apps.api.models.user import User


class Verification(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    document_file = FileField("Файл документа")
    confirmed = BooleanField("Подтверждён", default=False)

    class Meta:
        verbose_name = "Верификация"
        verbose_name_plural = "Верификация"

    def __str__(self):
        return ""
