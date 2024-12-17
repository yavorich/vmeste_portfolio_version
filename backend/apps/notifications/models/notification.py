from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.api.models import User, Event


class GroupNotification(models.Model):
    class Type(models.TextChoices):
        EVENT_REMIND = "EVENT_REMIND", "Напоминание о событии"
        EVENT_CANCELED = "EVENT_CANCELED", "Событие отменено"
        EVENT_CHANGED = "EVENT_CHANGED", "Событие изменено"
        EVENT_ADDED = "EVENT_ADDED", "Новое событие"
        EVENT_REC = "EVENT_REC", "Рекомендованное событие"
        ADMIN = "ADMIN", "От администрации"
        CHAT_JOIN = "CHAT_JOIN", "Пользователь присоединился к чату"

    type = models.CharField(_("Тип"), choices=Type.choices)
    created_at = models.DateTimeField(_("Время создания"), auto_now_add=True)
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="notifications",
        blank=True,
        null=True,
    )
    title = models.CharField(_("Заголовок"), max_length=50, null=True)
    body = models.TextField(_("Текст"), max_length=500, null=True)
    task_id = models.CharField(_("ID задачи"), max_length=255, blank=True, null=True)
    remind_hours = models.PositiveSmallIntegerField(
        _("Кол-во часов до начала"), blank=True, null=True
    )

    related_id = models.PositiveBigIntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"

    def get_users(self):
        users = User.objects.filter(is_active=True, is_staff=False, sending_push=True)
        if self.type == GroupNotification.Type.ADMIN:
            return users

        elif self.type == GroupNotification.Type.EVENT_REC:
            return users.filter(receive_recs=True)

        elif self.type == GroupNotification.Type.EVENT_REMIND:
            participants = self.event.participants.all()
            return users.filter(events__in=participants)

        elif self.type == GroupNotification.Type.EVENT_ADDED:
            categories = self.event.categories.all()
            organizer_user = self.event.organizer

            if organizer_user is not None:
                users = users.exclude(pk=organizer_user.pk)

            participants = self.event.participants.all()
            return (
                users.filter(categories__in=categories)
                .exclude(events__in=participants)
                .distinct()
            )

        elif self.type == GroupNotification.Type.CHAT_JOIN:
            participants = self.event.participants.all()
            if self.related_id is not None:
                users = users.exclude(pk=self.related_id)

            return users.filter(events__in=participants)

        else:
            participants = self.event.participants.filter(is_organizer=False)
            return users.filter(events__in=participants)

    def save(self, *args, **kwargs):
        if self.title is None:
            self.title = self.event.title
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class UserNotification(models.Model):
    notification = models.ForeignKey(
        GroupNotification,
        verbose_name="Уведомление",
        related_name="receivers",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        verbose_name="Пользователь",
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    title = models.CharField(_("Заголовок"), max_length=50, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(
        verbose_name=_("Событие"),
        to=Event,
        on_delete=models.CASCADE,
        related_name="user_notifications",
        blank=True,
        null=True,
    )
    body = models.TextField(_("Текст"), max_length=500, null=True)
    read = models.BooleanField(_("Прочитано"), default=False)

    @property
    def short_text(self):
        max_length = 50
        if len(self.title) <= max_length:
            return self.title
        else:
            return f"{self.title[:max_length-3]}..."

    def __str__(self) -> str:
        return f"{self.title}: для {self.user.get_full_name()}"

    def generate_remind_body(self):
        hours_sample = {
            "0": "Событие началось! Не забудьте подтвердить своё присутствие.",
            "1": "Событие начнется уже через час!",
            "4": "До начала события осталось 4 часа!",
            "24": "Напоминаем, что событие уже завтра!",
        }
        body = hours_sample[str(self.notification.remind_hours)]
        organizer = self.user == self.event.organizer
        event_remind_sample = "отменить" if organizer else "не пойти на"
        if self.notification.remind_hours > 3:
            body += (
                f" Вы можете {event_remind_sample} встречу. Успейте принять решение"
                + " не позднее, чем за 3 часа до начала мероприятия!"
            )
        return body

    def get_title(self):
        if self.event:
            return self.event.title
        return self.notification.title

    def get_body(self):
        if self.notification.type == GroupNotification.Type.EVENT_REMIND:
            return self.generate_remind_body()
        if self.notification.type == GroupNotification.Type.ADMIN:
            return self.notification.body
        if self.notification.type in (
            GroupNotification.Type.EVENT_REC,
            GroupNotification.Type.EVENT_ADDED,
        ):
            return (
                "Новое интересное событие! "
                + "Успейте записаться, пока есть свободные места."
            )
        if self.notification.type == GroupNotification.Type.EVENT_CANCELED:
            return "Событие отменено организатором или администрацией."
        if self.notification.type == GroupNotification.Type.EVENT_CHANGED:
            return (
                "Событие изменилось! "
                + "Проверьте актуальную информацию на странице события"
            )

    def save(self, *args, **kwargs):
        if self.title in (None, ""):
            self.title = self.get_title()
        if self.body in (None, ""):
            self.body = self.get_body()
        return super().save(*args, **kwargs)
