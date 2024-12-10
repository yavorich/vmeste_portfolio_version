from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.utils.timezone import timedelta, localtime
from asgiref.sync import async_to_sync

from config.celery import celery_app
from apps.api.models import Event, EventParticipant
from apps.notifications.models import GroupNotification, UserNotification
from apps.notifications.tasks import (
    user_notifications_task,
    send_push_notification,
)
from apps.notifications.serializers import UserNotificationMessageSerializer
from apps.notifications.services import send_ws_notification
from core.utils.old_instance import get_old_instance


@receiver([post_save], sender=EventParticipant)
def send_join_event_notification(
    sender, instance: EventParticipant, created: bool, **kwargs
):
    if created:
        title = instance.event.title
        if instance.is_organizer:
            body = f'Вы успешно создали событие: "{title}"'
        else:
            body = f'Вы успешно записались на событие: "{title}"'
        notification = UserNotification.objects.create(
            user=instance.user,
            event=instance.event,
            title=title,
            body=body,
        )
        async_to_sync(send_push_notification)(notification)


@receiver([post_save], sender=EventParticipant)
def send_kick_event_notification(sender, instance: EventParticipant, **kwargs):
    if instance.kicked_by_organizer:
        title = instance.event.title
        body = "Организатор события убрал вас из списка участников."
        notification = UserNotification.objects.create(
            user=instance.user,
            event=instance.event,
            title=title,
            body=body,
        )
        async_to_sync(send_push_notification)(notification)
        instance.delete()


@receiver([post_save], sender=Event)
def create_event_group_notifications(sender, instance: Event, created: bool, **kwargs):
    is_active = instance.is_active and not instance.is_draft
    if created and is_active:
        create_event_remind_notifications(instance)
    if not created:
        was_draft = instance.tracker.previous("is_draft")
        was_active = instance.tracker.previous("is_active") and not was_draft
        delete_existing_remind_notifications(instance)
        if is_active:
            create_event_remind_notifications(instance)
        elif was_active:
            create_event_cancel_notification(instance)


@receiver([pre_save], sender=Event)
def create_event_change_notification(instance: Event, **kwargs):
    if instance.pk is None or not instance.is_active or instance.is_draft:
        return

    old_instance = get_old_instance(instance)
    if old_instance is None:
        return

    for field in (
        "title",
        "location",
        "date",
        "start_time",
        "end_time",
        "max_age",
        "min_age",
        "theme",
        "total_male",
        "total_female",
        "short_description",
        "description",
        "is_close_event",
        "organizer_will_pay",
    ):
        if getattr(instance, field) != getattr(old_instance, field):
            create_event_change_notification(instance)
            return

    if instance.categories.values_list("id", flat=True).order_by(
        "id"
    ) != old_instance.categories.values_list("id", flat=True).order_by("id"):
        create_event_change_notification(instance)


def delete_existing_remind_notifications(instance: Event):
    GroupNotification.objects.filter(
        type=GroupNotification.Type.EVENT_REMIND, event=instance
    ).delete()


def create_event_remind_notifications(instance: Event):
    GroupNotification.objects.filter(
        type=GroupNotification.Type.EVENT_ADDED, event=instance
    ).delete()
    GroupNotification.objects.create(
        type=GroupNotification.Type.EVENT_ADDED, event=instance
    )

    for hours in [24, 4, 1, 0]:
        if instance.start_datetime - timedelta(hours=hours) > localtime():
            GroupNotification.objects.create(
                type=GroupNotification.Type.EVENT_REMIND,
                remind_hours=hours,
                event=instance,
            )


def create_event_cancel_notification(instance: Event):
    GroupNotification.objects.filter(
        event=instance, type=GroupNotification.Type.EVENT_CANCELED
    ).delete()
    GroupNotification.objects.create(
        event=instance, type=GroupNotification.Type.EVENT_CANCELED
    )
    if not instance.is_active:
        notification = UserNotification.objects.create(
            user=instance.organizer,
            event=instance,
            title=instance.title,
            body="Событие заблокировано администрацией",
        )
        async_to_sync(send_push_notification)(notification)


def create_event_change_notification(instance: Event):
    GroupNotification.objects.filter(
        event=instance, type=GroupNotification.Type.EVENT_CHANGED
    ).delete()
    GroupNotification.objects.create(
        event=instance, type=GroupNotification.Type.EVENT_CHANGED
    )


@receiver(post_save, sender=GroupNotification)
def create_user_notifications_task(
    sender, instance: GroupNotification, created: bool, **kwargs
):
    if created:
        if instance.type == GroupNotification.Type.EVENT_REMIND:
            delta = timedelta(hours=instance.remind_hours)
            task = user_notifications_task.apply_async(
                eta=instance.event.start_datetime - delta,
                args=[instance.pk],
            )
            instance.task_id = task.id
            instance.save()
        else:
            user_notifications_task.apply_async(args=[instance.pk], countdown=3)


@receiver(pre_delete, sender=GroupNotification)
def revoke_pending_task(sender, instance: GroupNotification, **kwargs):
    if instance.type == GroupNotification.Type.EVENT_REMIND:
        celery_app.control.revoke(task_id=instance.task_id)


@receiver(post_save, sender=UserNotification)
def send_unread_notifications_ws_message(sender, instance: UserNotification, **kwargs):
    serializer = UserNotificationMessageSerializer(instance=instance)
    send_ws_notification(serializer.data, instance.user.pk)
