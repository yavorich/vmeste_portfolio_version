import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import IntegrityError

from chat.models import ReadMessage
from api.models import Event


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            return await self.close(code=401)

        self.room_group_names = await self.get_user_groups()

        for group_name in self.room_group_names:
            await self.channel_layer.group_add(
                group_name,
                self.channel_name,
            )

        await self.accept()

    async def disconnect(self, code):
        if self.user.is_authenticated and hasattr(self, "room_group_names"):
            for group_name in self.room_group_names:
                await self.channel_layer.group_discard(
                    group_name,
                    self.channel_name,
                )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json["type"] == "read_message":
            await self.read_message(text_data_json)

        elif text_data_json["type"] == "chat_message":
            group_name = "chat_%s" % text_data_json["event"]["id"]
            await self.channel_layer.group_send(
                group_name,
                text_data_json,
            )

        elif text_data_json["type"] == "join_chat":
            await self.join_chat(text_data_json)

        elif text_data_json["type"] == "leave_chat":
            await self.leave_chat(text_data_json)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    async def join_chat(self, data):
        group_name = "chat_%s" % data["event_id"]
        await self.channel_layer.group_add(
            group_name,
            self.channel_name,
        )

    async def leave_chat(self, data):
        await self.channel_layer.group_discard(
            data["group"],
            self.channel_name,
        )

    @database_sync_to_async
    def read_message(self, data):
        try:
            ReadMessage.objects.get_or_create(
                user=data["user"],
                message=data["message"],
            )
        except IntegrityError:
            pass  # TODO: test

    @database_sync_to_async
    def get_user_groups(self):
        events = (
            Event.objects.filter_organizer_or_participant(self.user)
            .distinct()
            .filter_not_expired()
            .filter(is_active=True, is_draft=False)
        )
        with open("log.txt", "w") as f:
            f.write(
                str(["chat_%s" % id for id in events.values_list("id")])
                + "\n"
                + self.channel_name
            )
        return ["chat_%s" % id for id in events.values_list("id")]
