from django.contrib.admin.models import LogEntry
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.admin_history.models import HistoryLog


@receiver(post_save, sender=LogEntry)
def create_log_history(created, instance, **kwargs):
    if created:
        HistoryLog.objects.create(
            **{
                field: getattr(instance, field)
                for field in (
                    "action_time",
                    "user_id",
                    "content_type_id",
                    "object_id",
                    "object_repr",
                    "action_flag",
                    "change_message",
                )
            }
        )
