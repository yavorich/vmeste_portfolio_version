from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django_elasticsearch_dsl.registries import registry

from api.models import EventParticipant, Event, User, Location
from core.utils import delete_file, delete_file_on_update


@receiver(post_delete, sender=EventParticipant)
def update_event_document(sender, instance: EventParticipant, **kwargs):
    registry.update(instance.event)


@receiver(post_delete, sender=Event)
def delete_event_cover(sender, instance: Event, **kwargs):
    delete_file(instance, "cover")


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
