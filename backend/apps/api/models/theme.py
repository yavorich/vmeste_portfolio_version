from django.db import models
from django.utils.translation import gettext_lazy as _


class Theme(models.Model):
    title = models.CharField(_("Название"), max_length=255, unique=True)
    organizer_price = models.PositiveIntegerField(
        "Стоимость для организаторов", default=5
    )
    participant_price = models.PositiveIntegerField(
        "Стоимость для участников", default=1
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.title
