from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Q, F
from django.db.models.manager import BaseManager
from django.template.defaultfilters import date as _date
from django.template.defaultfilters import time as _time
from django.urls import reverse
from django.utils.timezone import localtime, timedelta, datetime
from django.utils.translation import gettext_lazy as _
from model_utils import FieldTracker
import os
import uuid as _uuid

from apps.api.enums import Gender
from core.model_fields import CompressedImageField
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
            free_places=models.Case(
                models.When(
                    total_people__isnull=False,
                    then=F("total_people") - participants_count,
                ),
                models.When(Q(total_male=None) | Q(total_female=None), then=None),
                default=F("total_male") + F("total_female") - participants_count,
            )
        )

    def get_free_places_by_gender(self, gender: Gender):
        total_field = "total_" + gender
        participants_count = models.Count(
            "participants",
            filter=Q(participants__user__gender=gender),
        )
        return self.annotate(
            free_places=models.Case(
                models.When(
                    total_people__isnull=False,
                    then=F("total_people") - participants_count,
                ),
                models.When(**{total_field: None}, then=None),
                default=F(total_field) - participants_count,
            )
        )

    def filter_has_free_places(self, gender: Gender | None = None):
        if gender is not None:
            return self.get_free_places_by_gender(gender).filter(free_places__gt=0)
        return self.get_free_places().filter(Q(free_places__gt=0) | Q(free_places=None))

    def filter_past(self, hours=0, days=90):
        return self.filter(
            start_datetime__lte=localtime() - timedelta(hours=hours),
            start_datetime__gte=localtime() - timedelta(days=days),
        )

    def filter_not_expired(self, days=90):
        return self.filter(
            start_datetime__gte=localtime() - timedelta(days=days),
        )

    def filter_upcoming(self):
        return self.filter(start_datetime__gt=datetime.now())

    def filter_participant(self, user: User):
        return self.filter(participants__user=user)

    def get_recommended_event(self):
        return (
            self.filter(is_active=True, is_draft=False)
            .filter_upcoming()
            .filter_has_free_places()
            .order_by("-free_places")
            .first()
        )


def get_upload_path(instance, filename):
    return os.path.join("events", str(instance.pk), "cover", filename)


def get_upload_path_medium(instance, filename):
    return os.path.join("events", str(instance.pk), "cover_medium", filename)


class Event(models.Model):
    is_close_event = models.BooleanField(_("Закрытое мероприятие"))
    uuid = models.UUIDField(default=_uuid.uuid4, unique=True, editable=False)
    title = models.CharField(_("Название"), max_length=30)
    max_age = models.PositiveSmallIntegerField(
        _("Макс. возраст"), validators=[MinValueValidator(13), MaxValueValidator(100)]
    )
    min_age = models.PositiveSmallIntegerField(
        _("Мин. возраст"), validators=[MinValueValidator(12), MaxValueValidator(99)]
    )
    cover = CompressedImageField(
        _("Обложка"),
        max_width=720,
        max_height=720,
        upload_to=get_upload_path,
        default="defaults/cover.jpg",
    )
    cover_medium = CompressedImageField(
        _("Обложка"),
        max_width=240,
        max_height=240,
        upload_to=get_upload_path_medium,
        default="defaults/cover.jpg",
    )
    short_description = models.CharField(_("Краткое описание"), max_length=80)
    description = models.CharField(_("Полное описание"), max_length=500)
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
    start_datetime = models.DateTimeField("Время начала", blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    theme = models.ForeignKey(
        verbose_name=_("Тема"),
        to=Theme,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
    )
    categories = models.ManyToManyField(
        verbose_name=_("Категории"), to=Category, related_name="events"
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
    total_male = models.PositiveSmallIntegerField(
        _("Всего мужчин"), null=True, blank=True
    )
    total_female = models.PositiveSmallIntegerField(
        _("Всего женщин"), null=True, blank=True
    )
    total_people = models.PositiveSmallIntegerField(
        _("Всего участников"), null=True, blank=True
    )
    did_organizer_marking = models.BooleanField(
        _("Организатор отметил присутствие"), default=False
    )

    organizer_will_pay = models.BooleanField(
        _("Организатор оплатит встречу"), null=True, blank=True
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
                {"error": "Максимальный возраст должен быть больше минимального"}
            )
        if self.city and self.country and self.city.country != self.country:
            raise ValidationError(
                {"error": "Указанный город не соответствует указанной стране"}
            )

    @property
    def stats_men(self):
        return self.get_stats(Gender.MALE)

    @property
    def stats_women(self):
        return self.get_stats(Gender.FEMALE)

    @property
    def stats_people(self):
        count = EventParticipant.objects.filter(event=self).count()
        total = self.max_people
        return f"{count}/{total}" if total is not None else str(count)

    @property
    def max_people(self):
        total = self.total_people
        if total is None:
            if self.total_male is not None and self.total_female is not None:
                return self.total_male + self.total_female
            elif self.total_male is not None:
                return self.total_male
            elif self.total_female is not None:
                return self.total_female

        return total

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
    def link(self):
        if self.is_close_event:
            return reverse("api:event-detail", kwargs={"event_pk": self.uuid})
        return reverse("api:event-detail", kwargs={"event_pk": self.pk})

    @property
    def organizer(self):
        try:
            return self.participants.get(is_organizer=True).user
        except EventParticipant.DoesNotExist:
            return None

    @property
    def sign_price(self):
        # if self.organizer_will_pay:
        #     return 0
        # elif self.organizer_will_pay is None:
        #     return
        # else:
        #     return self.theme.participant_price
        return

    def get_stats(self, gender: Gender):
        total_field = "total_" + gender
        participants = EventParticipant.objects.filter(event=self, user__gender=gender)
        total = getattr(self, total_field)
        count = participants.count()
        return f"{count}/{total}" if total is not None else str(count)

    def get_participants(self) -> BaseManager[EventParticipant]:
        return self.participants.all()

    def get_participants_by_gender(
        self, gender: Gender
    ) -> BaseManager[EventParticipant]:
        return self.participants.filter(user__gender=gender)

    def get_participant(self, user: User) -> EventParticipant | None:
        try:
            return self.participants.get(user=user)
        except EventParticipant.DoesNotExist:
            return None

    def get_free_places(self, gender: Gender | None = None) -> bool:
        if self.total_people is not None:
            return self.total_people - self.participants.count()

        if gender:
            total_field = "total_" + gender
            total_field_value = getattr(self, total_field)
            if total_field_value is None:
                return

            return total_field_value - self.get_participants_by_gender(gender).count()
        if self.total_male is None or self.total_female is None:
            return

        return self.total_male + self.total_female - self.get_participants().count()

    def is_valid_sign_and_edit_time(self) -> bool:
        start = self.start_datetime
        return localtime() <= start - timedelta(hours=3)

    def is_valid_age_to_sign(self, user: User) -> bool:
        return self.min_age <= user.age <= self.max_age

    def is_valid_media_time(self) -> bool:
        start = self.start_datetime
        return start + timedelta(days=90) >= localtime() >= start

    def save(self, *args, **kwargs):
        self.start_datetime = datetime.combine(
            self.date, self.start_time, tzinfo=localtime().tzinfo
        )
        self.end_datetime = datetime.combine(
            self.date + timedelta(days=1 if self.end_time <= self.start_time else 0),
            self.end_time,
            tzinfo=localtime().tzinfo,
        )
        return super().save(*args, **kwargs)


class EventAdminProxy(Event):
    class Meta:
        proxy = True
        verbose_name = "Событие"
        verbose_name_plural = "Старт событий"
