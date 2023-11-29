from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from .enums import Gender


class Theme(models.Model):
    title = models.CharField(_("Название"), max_length=255)


class Category(models.Model):
    title = models.CharField(_("Название"), max_length=255)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)


class Country(models.Model):
    name = models.CharField(_("Название"), max_length=255)


class City(models.Model):
    name = models.CharField(_("Название"), max_length=255)
    country = models.ForeignKey(
        Country, related_name="cities", on_delete=models.CASCADE
    )


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


class Event(models.Model):
    title = models.CharField(_("Название"), max_length=255)
    max_age = models.PositiveSmallIntegerField(_("Макс. возраст"))
    min_age = models.PositiveSmallIntegerField(_("Мин. возраст"))
    cover = models.TextField(_("Обложка"))  # base64
    short_description = models.CharField(_("Краткое описание"), max_length=255)
    location = models.ForeignKey(
        Location,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True
    )
    day_and_time = models.DateTimeField(_("Дата и время"))
    theme = models.ForeignKey(
        Theme, related_name="events", on_delete=models.SET_NULL, null=True
    )
    category = models.ForeignKey(
        Category, related_name="events", on_delete=models.SET_NULL, null=True
    )
    country = models.ForeignKey(
        Country, related_name="events", on_delete=models.SET_NULL, null=True
    )
    city = models.ForeignKey(
        City, related_name="events", on_delete=models.SET_NULL, null=True
    )
    published = models.BooleanField()

    def __str__(self) -> str:
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    gender = models.CharField(_("Пол"), choices=Gender.choices(), max_length=6)


class EventParticipants(models.Model):
    event = models.ForeignKey(
        Event, related_name="participants", on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        Profile, related_name="events", on_delete=models.CASCADE
    )
    is_organizer = models.BooleanField()
