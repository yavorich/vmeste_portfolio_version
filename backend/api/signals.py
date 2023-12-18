from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry
from django.utils.timezone import timedelta
from django_celery_results.models import TaskResult
from config.celery import celery_app

from api.models import EventParticipant, Event, Notification
from api.tasks import send_push_notifications_task


@receiver(post_delete, sender=EventParticipant)
def update_event_document(sender, instance: EventParticipant, **kwargs):
    registry.update(instance.event)


@receiver(pre_save, sender=Event)
def send_event_notifications(sender, instance: Event, **kwargs):
    if instance.pk is not None:
        send_push_notifications_task.delay(instance, Notification.Type.EVENT_CHANGED)
        previous = Event.objects.get(pk=instance.pk)
        if previous.start_datetime == instance.start_datetime:
            return
        revoke_existing_remind_notifications()
    for delta in [timedelta(days=1), timedelta(hours=4)]:
        send_push_notifications_task.apply_async(
            eta=instance.start_datetime - delta,
            args=[instance.pk, Notification.Type.EVENT_REMIND],
        )


@receiver(post_delete, sender=Event)
def send_cancel_event_notifications(sender, instance: Event, **kwargs):
    revoke_existing_remind_notifications(instance)
    send_push_notifications_task.delay(instance.pk, Notification.Type.EVENT_CANCELED)


def revoke_existing_remind_notifications(instance):
    tasks = TaskResult.objects.filter(
        task_args=[instance.pk, Notification.Type.EVENT_REMIND]
    ).exclude(status="SUCCESS")
    for task in tasks:
        celery_app.control.revoke(task_id=task.task_id)
