from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import timedelta, now
from celery import states
from celery.signals import before_task_publish
from django_celery_results.models import TaskResult

from config.celery import celery_app
from api.models import Event
from notifications.models import Notification
from notifications.tasks import create_notifications_task, send_push_notifications_task
from notifications.services import PushGroup


@before_task_publish.connect
def create_task_result_on_publish(sender=None, headers=None, body=None, **kwargs):
    if "task" not in headers:
        return

    TaskResult.objects.store_result(
        "application/json",
        "utf-8",
        headers["id"],
        None,
        states.PENDING,
        task_name=headers["task"],
        task_args=headers["argsrepr"],
        task_kwargs=headers["kwargsrepr"],
    )


@receiver([post_save], sender=Event)
def create_event_notifications(sender, instance: Event, created: bool, **kwargs):
    is_active = instance.is_active and not instance.is_draft

    if not created:
        was_active = not instance.tracker.previous(
            "is_draft"
        ) and instance.tracker.previous("is_active")
        revoke_existing_remind_notifications(instance)
        if not is_active:
            if was_active:
                return create_notifications_task.delay(
                    instance.pk, Notification.Type.EVENT_CANCELED
                )
            return
        create_notifications_task.delay(instance.pk, Notification.Type.EVENT_CHANGED)

    if is_active:
        for delta in [timedelta(days=1), timedelta(hours=4)]:
            if instance.start_datetime - delta > now():
                create_notifications_task.apply_async(
                    eta=instance.start_datetime - delta,
                    args=[instance.pk, Notification.Type.EVENT_REMIND],
                )
                print("Remind notifications have been scheduled")


def revoke_existing_remind_notifications(instance):
    tasks = TaskResult.objects.filter(
        task_args=str([instance.pk, Notification.Type.EVENT_REMIND.value])
    ).exclude(status="SUCCESS")
    for task in tasks:
        celery_app.control.revoke(task_id=task.task_id)
    print("Existing notifications have been revoked")


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
