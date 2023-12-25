from django.db.models.signals import post_delete, pre_save, post_save
from django.dispatch import receiver
from django.utils.timezone import timedelta
from django_celery_results.models import TaskResult
from config.celery import celery_app

from api.models import Event
from notifications.models import Notification
from notifications.tasks import create_notifications_task, send_push_notifications_task
from notifications.services import PushGroup
from notifications.serializers import NotificationSerializer


@receiver(pre_save, sender=Event)
def create_event_notifications(sender, instance: Event, **kwargs):
    if instance.pk is not None:
        create_notifications_task.delay(instance.pk, Notification.Type.EVENT_CHANGED)
        previous = Event.objects.get(pk=instance.pk)
        if previous.start_datetime == instance.start_datetime:
            return
        revoke_existing_remind_notifications()
    for delta in [timedelta(days=1), timedelta(hours=4)]:
        create_notifications_task.apply_async(
            eta=instance.start_datetime - delta,
            args=[instance.pk, Notification.Type.EVENT_REMIND],
        )


@receiver(post_delete, sender=Event)
def create_cancel_event_notifications(sender, instance: Event, **kwargs):
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
    serializer = NotificationSerializer(instance=instance)
    groups = {
        Notification.Type.ADMIN: [PushGroup.ALL],
        Notification.Type.EVENT_REC: [PushGroup.ALL],
        Notification.Type.EVENT_CHANGED: [PushGroup.PARTICIPANTS],
        Notification.Type.EVENT_CANCELED: [PushGroup.PARTICIPANTS],
        Notification.Type.EVENT_REMIND: [PushGroup.PARTICIPANTS, PushGroup.ORGANIZER],
    }
    send_push_notifications_task.delay(serializer.data, groups[instance.type])
