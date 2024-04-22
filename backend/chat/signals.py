from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete, post_delete

from api.models import Event, EventParticipant, User
from chat.models import Message, Chat, ReadMessage
from chat.utils import (
    send_ws_message,
    # add_user_to_group,
    remove_user_from_group,
    send_ws_unread_messages,
)
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
    event_pk = instance.event.id
    send_ws_message(message_serializer.data, event_pk)
    for participant in instance.event.participants.all():
        message.read.get_or_create(user=participant.user)


@receiver(post_save, sender=EventParticipant)
def send_join_message(sender, instance: EventParticipant, created: bool, **kwargs):
    if created:
        print("USER JOINED")
        send_info_message(instance, join=True)


@receiver(pre_delete, sender=EventParticipant)
def send_leave_message(sender, instance: EventParticipant, **kwargs):
    print("USER LEFT")
    try:
        send_info_message(instance, join=False)
    except (Event.DoesNotExist, Chat.DoesNotExist, User.DoesNotExist):
        pass
    remove_user_from_group(instance.event)


# @receiver(post_save, sender=Event)
# def create_chat_group(sender, instance: Event, created: bool, **kwargs):
#     if created:
#         add_user_to_group(instance)


@receiver(post_delete, sender=Event)
def delete_chat_group(sender, instance: Event, **kwargs):
    remove_user_from_group(instance)


@receiver(post_delete, sender=Chat)
def delete_chat_event(sender, instance: Chat, **kwargs):
    try:
        instance.event.delete()
    except Event.DoesNotExist:
        pass


@receiver(post_save, sender=ReadMessage)
def send_unread_messages_ws_message(
    sender, instance: ReadMessage, created: bool, **kwargs
):
    serializer = MessageSerializer(
        instance=instance.message, context={"user": instance.user}
    )
    send_ws_unread_messages(serializer.data, instance.user.pk)
