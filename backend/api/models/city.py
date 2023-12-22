from django.db import models
from django.utils.translation import gettext_lazy as _

from .country import Country


class City(models.Model):
    name = models.CharField(_("Название"), max_length=255, unique=True)
    country = models.ForeignKey(
        Country, related_name="cities", on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.name
