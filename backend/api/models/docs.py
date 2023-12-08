from django.db import models
from django.utils.translation import gettext_lazy as _


class Docs(models.Model):
    class Name(models.TextChoices):
        RULES = "rules", "Правила"
        AGREEMENT = "agreement", "Соглашение"

    name = models.CharField(
        _("Тип документа"), choices=Name.choices, max_length=10, unique=True
    )
    text = models.TextField()
