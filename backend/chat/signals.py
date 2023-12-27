from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from api.models import EventParticipant
from chat.models import Message
from chat.utils import send_ws_message
from chat.serializers import MessageSerializer


def send_info_message(instance: EventParticipant, join: bool):
    text_sample = "присоединился к чату" if join else "покинул чат"
    message = Message.objects.create(
        chat=instance.event.chat,
        sender=instance.user,
        text=f"{instance.user.get_full_name()} {text_sample}",
        is_info=True,
        is_incoming=join,
    )
    message_serializer = MessageSerializer(
        instance=message, context={"user": instance.user}
    )
    event_id = instance.event.id
    send_ws_message(message_serializer.data, event_id)


@receiver(post_save, sender=EventParticipant)
def send_join_message(sender, instance: EventParticipant, created: bool, **kwargs):
    if created:
        send_info_message(instance, join=True)


@receiver(post_delete, sender=EventParticipant)
def send_leave_message(sender, instance: EventParticipant, **kwargs):
    send_info_message(instance, join=False)
