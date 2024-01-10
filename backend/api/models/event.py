from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q, F, Value
from django.db.models.functions import Concat, Cast
from django.db.models.manager import BaseManager
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.urls import reverse
from django.utils.timezone import now, timedelta, datetime
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
import os
import uuid as _uuid

from api.enums import Gender
from .location import Location
from .theme import Theme
from .category import Category
from .city import City
from .country import Country
from .participant import EventParticipant
from .user import User


class EventQuerySet(models.QuerySet):
    def get_free_places(self):
        participants_count = models.Count("participants")
        return self.annotate(
            free_places=F("total_male") + F("total_female") - participants_count
        )

    def get_free_places_by_gender(self, gender: Gender):
        total_field = "total_" + gender
        participants_count = models.Count(
            "participants",
            filter=Q(participants__user__gender=gender),
        )
        return self.annotate(free_places=F(total_field) - participants_count)

    def filter_has_free_places(self, gender: Gender | None = None):
        if gender is not None:
            return self.get_free_places_by_gender(gender).filter(free_places__gt=0)
        return self.get_free_places().filter(free_places__gt=0)

    def get_start_datetime(self):
        return self.annotate(
            start=Cast(
                Concat("date", Value(" "), "start_time"),
                output_field=models.DateTimeField(),
            )
        )

    def filter_past(self, hours=0, days=90):
        return self.get_start_datetime().filter(
            start__lte=now() - timedelta(hours=hours),
            start__gte=now() - timedelta(days=days),
        )

    def filter_not_expired(self, days=90):
        return self.get_start_datetime().filter(
            start__gte=now() - timedelta(days=days),
        )

    def filter_upcoming(self):
        return self.get_start_datetime().filter(start__gt=now())

    def filter_organizer_or_participant(self, user: User):
        return self.filter(Q(participants__user=user) | Q(organizer=user))


def get_upload_path(instance, filename):
    return os.path.join("events", str(instance.pk), "cover", filename)


class Event(models.Model):
    is_close_event = models.BooleanField(_("Закрытое мероприятие"))
    uuid = models.UUIDField(default=_uuid.uuid4, unique=True, editable=False)
    title = models.CharField(_("Название"), max_length=255)
    max_age = models.PositiveSmallIntegerField(
        _("Макс. возраст"), validators=[MinValueValidator(13), MaxValueValidator(100)]
    )
    min_age = models.PositiveSmallIntegerField(
        _("Мин. возраст"), validators=[MinValueValidator(12), MaxValueValidator(99)]
    )
    cover = models.ImageField(_("Обложка"), upload_to=get_upload_path)
    short_description = models.CharField(_("Краткое описание"), max_length=80)
    description = models.TextField(_("Полное описание"), max_length=1000)
    location = models.ForeignKey(
        verbose_name=_("Место"),
        to=Location,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
    )
    date = models.DateField(_("Дата"))
    start_time = models.TimeField(_("Время начала"))
    end_time = models.TimeField(_("Время завершения"))
    theme = models.ForeignKey(
        verbose_name=_("Категория"),
        to=Theme,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
    )
    categories = models.ManyToManyField(
        verbose_name=_("Подкатегория"), to=Category, related_name="events"
    )
    country = models.ForeignKey(
        verbose_name=_("Страна"),
        to=Country,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
    )
    city = models.ForeignKey(
        verbose_name=_("Город"),
        to=City,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
    )
    is_draft = models.BooleanField(_("Черновик"))
    is_active = models.BooleanField(_("Активное"), default=True)
    total_male = models.PositiveSmallIntegerField(_("Всего мужчин"))
    total_female = models.PositiveSmallIntegerField(_("Всего женщин"))
    organizer = models.ForeignKey(
        verbose_name=_("Организатор"),
        to=User,
        related_name="organized_events",
        on_delete=models.CASCADE,
    )
    did_organizer_marking = models.BooleanField(
        _("Организатор отметил присутствие"), default=False
    )
    tracker = FieldTracker()
    objects = EventQuerySet.as_manager()

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "События"
        ordering = ["date"]

    def __str__(self) -> str:
        return str(self.title)

    def clean(self):
        if self.min_age >= self.max_age:
            raise ValidationError(
                "Максимальный возраст должен быть больше минимального"
            )
        if self.city.country != self.country:
            raise ValidationError("Указанный город не соответствует указанной стране")

    @property
    def stats_men(self):
        return self.get_stats(Gender.MALE)

    @property
    def stats_women(self):
        return self.get_stats(Gender.FEMALE)

    @property
    def date_and_time(self):
        return _date(self.date, "j E") + _time(self.start_time, ", H:i")

    @property
    def date_and_year(self):
        return _date(self.date, "j E, Y")

    @property
    def day_and_time(self):
        return (
            _date(self.date, "l")
            + _time(self.start_time, ", H:i")
            + _time(self.end_time, "-H:i")
        )

    @property
    def start_datetime(self):
        return datetime.combine(self.date, self.start_time, tzinfo=now().tzinfo)

    @property
    def link(self):
        if self.is_close_event:
            return reverse("api:event-detail", kwargs={"event_pk": self.uuid})
        return reverse("api:event-detail", kwargs={"event_pk": self.pk})

    def get_stats(self, gender: Gender):
        total_field = "total_" + gender
        participants = EventParticipant.objects.filter(event=self, user__gender=gender)
        total = getattr(self, total_field)
        count = participants.count()
        return f"{count}/{total}"

    def get_participants(self) -> BaseManager[EventParticipant]:
        return self.participants.all()

    def get_participants_by_gender(
        self, gender: Gender
    ) -> BaseManager[EventParticipant]:
        return self.participants.filter(user__gender=gender)

    def get_participant(self, user: User) -> EventParticipant | None:
        try:
            return EventParticipant.objects.get(event=self, user=user)
        except EventParticipant.DoesNotExist:
            return None

    def get_free_places(self, gender: Gender | None = None) -> bool:
        if gender:
            total_field = "total_" + gender
            return (
                getattr(self, total_field)
                - self.get_participants_by_gender(gender).count()
            )
        return self.total_male + self.total_female - self.get_participants().count()

    def is_valid_sign_time(self) -> bool:
        start = self.start_datetime
        return now() <= start - timedelta(hours=3)

    def is_valid_media_time(self) -> bool:
        start = self.start_datetime
        return start + timedelta(days=90) >= now() >= start
