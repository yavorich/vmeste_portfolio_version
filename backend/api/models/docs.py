from django.db import models
from django.utils.translation import gettext_lazy as _


class Docs(models.Model):
    class Name(models.TextChoices):
        RULES = "rules", "Правила"
        AGREEMENT = "agreement", "Соглашение"
        OFFER = "offer", "Оферта"

    name = models.CharField(
        _("Тип документа"), choices=Name.choices, max_length=10, unique=True
    )
    text = models.TextField()

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self) -> str:
        return Docs.Name(self.name).label
