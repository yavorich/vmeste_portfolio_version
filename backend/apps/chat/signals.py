from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver

from apps.api.models import Event, EventParticipant, EventAdminProxy, User
from apps.chat.models import Message, Chat
from apps.chat.serializers import MessageSerializer
from apps.chat.utils import (
    send_ws_message,
    # add_user_to_group,
    remove_user_from_group,
)
from apps.notifications.models import GroupNotification


def send_info_message(instance: EventParticipant, join: bool):
    text_sample = "присоединился к чату" if join else "покинул чат"
    text = f"{instance.user.get_full_name()} {text_sample}"
    message = Message.objects.create(
        chat=instance.event.chat,
        sender=instance.user,
        text=text,
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

    if join:
        GroupNotification.objects.create(
            type=GroupNotification.Type.CHAT_JOIN,
            event=instance.event,
            related_id=instance.user_id,
            body=text,
        )


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
@receiver(post_delete, sender=EventAdminProxy)
def delete_chat_group(sender, instance: Event, **kwargs):
    remove_user_from_group(instance)


@receiver(post_delete, sender=Chat)
def delete_chat_event(sender, instance: Chat, **kwargs):
    try:
        instance.event.delete()
    except Event.DoesNotExist:
        pass
