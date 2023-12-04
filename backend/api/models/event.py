from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.manager import BaseManager
from django.utils.timezone import now, timedelta
from .location import Location
from .theme import Theme
from .category import Category
from .city import City
from .country import Country
from .eventparticipant import EventParticipant
from .user import User


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

    def get_participants(self) -> BaseManager[EventParticipant]:
        return EventParticipant.objects.filter(event=self, is_organizer=False)

    def get_participant(self, user: User) -> EventParticipant | None:
        try:
            return EventParticipant.objects.get(event=self, user=user)
        except EventParticipant.DoesNotExist:
            return None

    def get_organizer(self) -> EventParticipant:
        return EventParticipant.objects.get(event=self, is_organizer=True)

    def has_free_places(self) -> bool:
        return self.num_places > self.get_participants().count()

    def is_valid_sign_time(self) -> bool:
        return now() <= self.start_datetime - timedelta(hours=3)
