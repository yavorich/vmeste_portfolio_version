from django.db import models
from django.utils.translation import gettext_lazy as _
from .country import Country
from .city import City


class Location(models.Model):
    name = models.CharField(_("Название"), max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(_("Адрес"), max_length=255)
    country = models.ForeignKey(
        Country, related_name="locations", on_delete=models.CASCADE
    )
    city = models.ForeignKey(
        City, related_name="locations", on_delete=models.CASCADE
    )
