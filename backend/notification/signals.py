from django.db.models.signals import post_save
from django.dispatch import receiver

from notification.models import Notification
from notification.tasks import send_push_notifications_task


@receiver(post_save, sender=Notification)
def send_push_notifications(sender, instance, created, **kwargs):
    if created:
        send_push_notifications_task.delay(instance.title, instance.body)
