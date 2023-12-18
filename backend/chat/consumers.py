import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import IntegrityError

from chat.models import ReadMessage


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

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "read_message":
            await self.read_message(text_data_json)

        elif text_data_json["type"] == "send_message":
            await self.channel_layer.group_send(
                self.room_group_name,
                text_data_json,
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def read_message(self, data):
        try:
            ReadMessage.objects.create(
                user=data["user"],
                message=data["message"],
            )
        except IntegrityError:
            pass  # TODO: test
