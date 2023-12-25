from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils.timezone import timedelta, now
from django_celery_results.models import TaskResult
from config.celery import celery_app

from api.models import Event
from notifications.models import Notification
from notifications.tasks import create_notifications_task, send_push_notifications_task
from notifications.services import PushGroup


@receiver([post_save], sender=Event)
def create_event_notifications(sender, instance: Event, **kwargs):
    if instance.pk is None:
        return

    revoke_existing_remind_notifications(instance)

    if not instance.is_active or instance.is_draft:
        create_notifications_task.delay(instance.pk, Notification.Type.EVENT_CANCELED)
        return

    create_notifications_task.delay(instance.pk, Notification.Type.EVENT_CHANGED)

    for delta in [timedelta(days=1), timedelta(hours=4)]:
        if instance.start_datetime - delta > now():
            create_notifications_task.apply_async(
                eta=instance.start_datetime - delta,
                args=[instance.pk, Notification.Type.EVENT_REMIND],
            )


@receiver(pre_delete, sender=Event)
def create_event_notifications_on_delete(sender, instance: Event, **kwargs):
    revoke_existing_remind_notifications(instance)
    create_notifications_task.delay(instance.pk, Notification.Type.EVENT_CANCELED)


def revoke_existing_remind_notifications(instance):
    tasks = TaskResult.objects.filter(
        task_args=[instance.pk, Notification.Type.EVENT_REMIND]
    ).exclude(status="SUCCESS")
    for task in tasks:
        celery_app.control.revoke(task_id=task.task_id)


@receiver(post_save, sender=Notification)
def send_push_notifications(sender, instance, **kwargs):
    groups = {
        Notification.Type.ADMIN: [PushGroup.ALL],
        Notification.Type.EVENT_REC: [PushGroup.ALL],
        Notification.Type.EVENT_CHANGED: [PushGroup.PARTICIPANTS],
        Notification.Type.EVENT_CANCELED: [PushGroup.PARTICIPANTS],
        Notification.Type.EVENT_REMIND: [PushGroup.PARTICIPANTS, PushGroup.ORGANIZER],
    }
    send_push_notifications_task.delay(instance.pk, groups[instance.type])
