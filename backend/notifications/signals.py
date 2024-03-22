from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import timedelta, localtime

from config.celery import celery_app
from api.models import Event, EventParticipant
from notifications.models import GroupNotification, UserNotification
from notifications.tasks import (
    user_notifications_task,
    push_notification,
)


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
        push_notification(notification)


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
            create_event_change_notification(instance)
            create_event_remind_notifications(instance)
        elif was_active:
            create_event_cancel_notification(instance)


def delete_existing_remind_notifications(instance: Event):
    GroupNotification.objects.filter(
        type=GroupNotification.Type.EVENT_REMIND, event=instance
    ).delete()


def create_event_remind_notifications(instance: Event):
    for hours in [24, 4, 1]:
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
            user_notifications_task.delay(instance.pk)


@receiver(pre_delete, sender=GroupNotification)
def revoke_pending_task(sender, instance: GroupNotification, **kwargs):
    if instance.type == GroupNotification.Type.EVENT_REMIND:
        celery_app.control.revoke(task_id=instance.task_id)
