import mimetypes
from django.db.models.signals import post_delete, pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django_elasticsearch_dsl.registries import registry

from api.models import EventParticipant, Event, User, Location, EventMedia
from api.services import generate_video_preview
from api.services.payment import (
    do_payment_on_create,
    do_payment_on_update,
    do_payment_refund,
)
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
def delete_event_cover_and_media(sender, instance: Event, **kwargs):
    delete_file(instance, "cover")
    for media in instance.media.all():
        delete_file(media, "file")
        delete_file(media, "preview")


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


@receiver(post_save, sender=EventMedia)
def add_media_info(sender, instance: EventMedia, created: bool, **kwargs):
    if created:
        instance.mimetype = mimetypes.guess_type(instance.file.url)[0].split("/")[0]
        if instance.mimetype == "video":
            instance.preview = generate_video_preview(instance)
        instance.save()


@receiver(pre_save, sender=Event)
def do_payment(sender, instance: Event, **kwargs):
    if instance._state.adding or not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    do_payment_on_update(old_instance, instance)


@receiver(pre_delete, sender=Event)
def refund_payment(sender, instance, **kwargs):
    if timezone.now() < instance.start_datetime:
        do_payment_refund(instance)
