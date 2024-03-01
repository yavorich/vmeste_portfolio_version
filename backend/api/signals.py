from django.db.models.signals import post_delete, pre_save, post_save, pre_delete
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from api.models import EventParticipant, Event, User, Location
from chat.models import Chat
from core.utils import delete_file, delete_file_on_update


@receiver(post_delete, sender=EventParticipant)
def update_event_document(sender, instance: EventParticipant, **kwargs):
    registry.update(instance.event)


@receiver(post_delete, sender=EventParticipant)
def delete_organized_events(sender, instance: EventParticipant, **kwargs):
    if instance.is_organizer:
        instance.event.delete()


@receiver(post_delete, sender=Event)
def delete_event_cover(sender, instance: Event, **kwargs):
    delete_file(instance, "cover")


@receiver(post_delete, sender=Event)
def delete_event_notifications(sender, instance: Event, **kwargs):
    instance.notifications.all().delete()


@receiver(pre_save, sender=Event)
def update_event_cover(sender, instance, **kwargs):
    delete_file_on_update(sender, instance, "cover", **kwargs)


@receiver(post_delete, sender=Location)
def delete_location_cover(sender, instance: Location, **kwargs):
    delete_file(instance, "cover")


@receiver(pre_save, sender=Location)
def update_location_cover(sender, instance, **kwargs):
    delete_file_on_update(sender, instance, "cover", **kwargs)


@receiver(post_delete, sender=User)
def delete_user_avatar(sender, instance: User, **kwargs):
    delete_file(instance, "avatar")


@receiver(pre_save, sender=User)
def update_user_avatar(sender, instance, **kwargs):
    delete_file_on_update(sender, instance, "avatar", **kwargs)


@receiver(pre_delete, sender=User)
def delete_user_events(sender, instance: User, **kwargs):
    instance.events.all().delete()


@receiver(post_save, sender=Event)
def create_event_chat(sender, instance: Event, created, **kwargs):
    if created:
        Chat.objects.create(event=instance)


@receiver(post_save, sender=User)
def delete_blocked_user_events(sender, instance: User, **kwargs):
    if not instance.is_active:
        instance.events.all().delete()
