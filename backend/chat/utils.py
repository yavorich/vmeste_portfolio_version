from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.models import Message

channel_layer = get_channel_layer()


@async_to_sync
async def send_ws_message(message, event_pk):
    await asend_ws_message(message, event_pk, channel_layer)


async def asend_ws_message(message: Message, event_pk, _channel_layer):
    with open("log.txt", "a") as f:
        f.write(f"Sending message from utils: {message}\n")
    await _channel_layer.group_send(
        "chat_%s" % event_pk,
        {
            "type": "chat_message",
            "message": message,
        },
    )


# @async_to_sync
# async def add_user_to_group(event):
#     group_name = "chat_%s" % event.pk
#     await channel_layer.group_send(
#         group_name,
#         {
#             "type": "join_chat",
#             "event_pk": group_name,
#         }
#     )


@async_to_sync
async def remove_user_from_group(event):
    group_name = "chat_%s" % event.pk
    await channel_layer.group_send(
        group_name,
        {
            "type": "leave_chat",
            "group": group_name,
        }
    )
