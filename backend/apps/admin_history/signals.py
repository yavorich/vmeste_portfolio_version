from django.contrib.admin.models import LogEntry
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from apps.admin_history.models import HistoryLog


post_bulk_create = Signal()


def bulk_create_decorator(model):
    def bulk_create(*args, **kwargs):
        objs = super(
            model._default_manager.__class__, model._default_manager
        ).bulk_create(*args, **kwargs)
        post_bulk_create.send(sender=model, instances=objs)
        return objs

    return bulk_create


LogEntry.objects.bulk_create = bulk_create_decorator(LogEntry)


def get_object_data(lof_entry):
    model = lof_entry.content_type.model_class()
    history_fields = (
        model._meta.history_fields if hasattr(model._meta, "history_fields") else {}
    )

    if len(history_fields) > 0:
        try:
            obj = model.objects.get(pk=lof_entry.object_id)
            return {field: str(getattr(obj, field)) for field in history_fields}
        except ObjectDoesNotExist:
            pass

    return {}


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
            },
            object_data=get_object_data(instance),
        )


@receiver(post_bulk_create, sender=LogEntry)
def bulk_create_log_history(instances, **kwargs):
    HistoryLog.objects.bulk_create(
        [
            HistoryLog(
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
                },
                object_data=get_object_data(instance),
            )
            for instance in instances
        ]
    )
