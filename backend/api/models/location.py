from django.db import models
from django.utils.translation import gettext_lazy as _

from .country import Country
from .city import City


class Location(models.Model):
    class Status(models.TextChoices):
        VERIFIED = "verified", "Подтверждено"
        RECOMMENDED = "recommended", "Рекомендовано"
        UNKNOWN = "unknown", "Неизвестно"
    cover = models.TextField(_("Обложка"))  # base64
    name = models.CharField(_("Название"), max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(_("Адрес"), max_length=255)
    country = models.ForeignKey(
        Country, related_name="locations", on_delete=models.CASCADE
    )
    city = models.ForeignKey(City, related_name="locations", on_delete=models.CASCADE)
    status = models.CharField(choices=Status.choices, max_length=11)
    discount = models.IntegerField(_("Скидка"), default=0)

    @property
    def coords_field_indexing(self):
        """Coords for indexing.
        Used in Elasticsearch indexing/tests of `geo_distance` native filter.
        """
        return {
            'lat': self.latitude,
            'lon': self.longitude,
        }
