from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import os

from apps.api.models.user import User
from .country import Country
from .city import City


def get_upload_path(instance, filename):
    return os.path.join("locations", str(instance.pk), "cover", filename)


class Location(models.Model):
    class Status(models.TextChoices):
        VERIFIED = "verified", "Подтверждено"
        RECOMMENDED = "recommended", "Рекомендовано"
        UNKNOWN = "unknown", "Неизвестно"

    cover = models.ImageField(
        _("Обложка"), upload_to=get_upload_path, default="defaults/cover.jpg"
    )
    name = models.CharField(_("Название"), max_length=255)
    latitude = models.FloatField(
        _("Широта"), validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        _("Долгота"), validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )
    address = models.CharField(_("Адрес"), max_length=255)
    country = models.ForeignKey(
        Country,
        related_name="locations",
        on_delete=models.CASCADE,
        verbose_name=_("Страна"),
    )
    city = models.ForeignKey(
        City,
        related_name="locations",
        on_delete=models.CASCADE,
        verbose_name=_("Город"),
    )
    status = models.CharField(_("Статус"), choices=Status.choices, max_length=11)
    discount = models.IntegerField(_("Скидка"), default=0)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Добавил"
    )

    class Meta:
        verbose_name = "Локация"
        verbose_name_plural = "Локации"
        history_fields = {"address": "Адрес"}

    def __str__(self):
        return self.name

    @property
    def coords_field_indexing(self):
        """Coords for indexing.
        Used in Elasticsearch indexing/tests of `geo_distance` native filter.
        """
        return {
            "lat": self.latitude,
            "lon": self.longitude,
        }
