import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

logger = logging.getLogger("ws")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.id = self.scope["url_route"]["kwargs"]["event_id"]
        self.room_group_name = "chat_%s" % self.id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()
        logger.debug(
            f"WS CONN USER={self.user}, CHAT={self.id}, GROUP={self.room_group_name}"
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        logger.debug("Message received")
        await self.channel_layer.group_send(
            self.room_group_name,
            text_data_json,
        )

    async def chat_message(self, event):
        logger.debug("Message sending to each group member")
        await self.send(text_data=json.dumps(event))
