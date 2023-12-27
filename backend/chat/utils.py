from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.models import Message

channel_layer = get_channel_layer()


@async_to_sync
async def send_ws_message(message, event_id):
    await asend_ws_message(message, event_id, channel_layer)


async def asend_ws_message(message: Message, event_id, _channel_layer):
    await _channel_layer.group_send(
        "chat_%s" % event_id,
        {
            "type": "chat_message",
            "message": message,
        }
    )
