from django.db import models
from django.utils.translation import gettext_lazy as _
from .location import Location
from .theme import Theme
from .category import Category
from .city import City
from .country import Country


class Event(models.Model):
    title = models.CharField(_("Название"), max_length=255)
    max_age = models.PositiveSmallIntegerField(_("Макс. возраст"))
    min_age = models.PositiveSmallIntegerField(_("Мин. возраст"))
    cover = models.TextField(_("Обложка"))  # base64
    description = models.TextField(_("Описание"))
    location = models.ForeignKey(
        Location, related_name="events", on_delete=models.SET_NULL, null=True
    )
    start_datetime = models.DateTimeField(_("Начало"))
    end_datetime = models.DateTimeField(_("Конец"))
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
    num_places = models.PositiveSmallIntegerField()
    link = models.URLField()
    did_organizer_marking = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.title
