import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import IntegrityError
from asgiref.sync import sync_to_async

from chat.models import ReadMessage
from api.models import Event


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.id = self.scope["url_route"]["kwargs"]["event_pk"]
        self.user = self.scope["user"]

        try:
            event = await Event.objects.aget(id=self.id)
        except Event.DoesNotExist:
            return await self.close(code=404)

        if not self.user.is_authenticated:
            return await self.close(code=401)

        if not (
            self.user == await sync_to_async(getattr)(event, "organizer")
            or await sync_to_async(event.get_participant)(self.user)
        ):
            return await self.close(code=403)

        self.room_group_name = "chat_%s" % self.id
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        if self.user.is_authenticated and hasattr(self, "room_group_name"):
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
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    @database_sync_to_async
    def read_message(self, data):
        try:
            ReadMessage.objects.get_or_create(
                user=data["user"],
                message=data["message"],
            )
        except IntegrityError:
            pass  # TODO: test
