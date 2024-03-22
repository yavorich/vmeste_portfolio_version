import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db import transaction
from django.db.models import Q
from asgiref.sync import async_to_sync

from chat.models import ReadMessage, Message, Chat
from chat.serializers import MessageSendSerializer, MessageSerializer
from chat.utils import send_ws_message
from notifications.models import UserNotification
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
        await self.send_unread_notifications()

    async def send_unread_notifications(self):
        unread = await self.get_unread_notifications_count()
        await self.channel_layer.group_send(
            "user_%s" % self.user.id,
            {
                "type": "notifications",
                "unread": unread,
            },
        )

    async def disconnect(self, code):
        if self.user.is_authenticated and hasattr(self, "room_group_names"):
            for group_name in self.room_group_names:
                await self.channel_layer.group_discard(
                    group_name,
                    self.channel_name,
                )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        _type = text_data_json["type"]

        if _type == "read_message":
            await self.read_message(text_data_json)

        elif _type == "read_notification":
            await self.read_notification(text_data_json)

        elif _type == "chat_message":
            await self.save_and_send_message(text_data_json)

        elif _type == "chat_notifications":
            await self.chat_notifications(text_data_json)

        elif _type == "join_chat":
            await self.join_chat(text_data_json)

        elif _type == "leave_chat":
            await self.leave_chat(text_data_json)

    async def chat_message(self, event):
        with open("log.txt", "a") as f:
            event = await self.add_user_info(event)
            f.write(f"Sending message from chat_message to {self.user}: {event}\n")
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    async def user_notification(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    async def notifications(self, event):
        await self.send(text_data=json.dumps(event, ensure_ascii=False))

    @database_sync_to_async
    def add_user_info(self, data):
        # TODO: попробовать без этого
        with transaction.atomic():
            is_mine = self.user.id == data["message"]["sender"]["id"]

            data["message"]["is_mine"] = is_mine

            chat = Chat.objects.get(pk=data["message"]["chat"])
            participant = chat.event.get_participant(user=self.user)
            data["message"]["send_notification"] = participant.chat_notifications
            data["message"]["unread"] = chat.messages.filter(
                ~Q(read__user=self.user)
            ).count()
            return data

    @database_sync_to_async
    def save_and_send_message(self, data):
        try:
            chat = Chat.objects.get(pk=data["message"]["event_id"])
        except Chat.DoesNotExist:
            return

        if not chat.event.get_participant(user=self.user):
            return

        send_serializer = MessageSendSerializer(
            data=data["message"],
            context={
                "chat": chat,
                "sender": self.user,
                "is_info": False,
                "is_incoming": False,
            },
        )
        send_serializer.is_valid(raise_exception=True)
        message = send_serializer.save()
        ReadMessage.objects.get_or_create(message=message, user=message.sender)

        headers = dict(self.scope["headers"])
        message_serializer = MessageSerializer(
            instance=message, context={"user": self.user, "headers": headers}
        )
        with open("log.txt", "a") as f:
            f.write(f"Sending message from consumer: {message_serializer.data}\n")

        send_ws_message(message_serializer.data, chat.pk)

    async def join_chat(self, data):
        group_name = "chat_%s" % data["event_id"]
        with open("log.txt", "a") as f:
            f.write(f"{self.user} connected to group: {group_name}\n")
        await self.channel_layer.group_add(
            group_name,
            self.channel_name,
        )

    async def leave_chat(self, data):
        with open("log.txt", "a") as f:
            f.write(f"{self.user} disconnected from group: {data['group']}\n")
        await self.channel_layer.group_discard(
            data["group"],
            self.channel_name,
        )

    @database_sync_to_async
    def read_message(self, data):
        try:
            message = Message.objects.get(id=data["message_id"])
        except Message.DoesNotExist:
            return
        ReadMessage.objects.get_or_create(
            user=self.user,
            message=message,
        )

    @database_sync_to_async
    def read_notification(self, data):
        try:
            notification = UserNotification.objects.get(id=data["notification_id"])
        except UserNotification.DoesNotExist:
            return
        notification.read = True
        notification.save()
        async_to_sync(self.send_unread_notifications())

    @database_sync_to_async
    def chat_notifications(self, data):
        try:
            chat = Chat.objects.get(pk=data["chat_id"])
        except Chat.DoesNotExist:
            return

        participant = chat.event.get_participant(user=self.user)
        if not participant:
            return

        participant.chat_notifications = data["enabled"]
        participant.save()

    @database_sync_to_async
    def get_user_groups(self):
        events = (
            Event.objects.filter_participant(self.user)
            .distinct()
            .filter_not_expired()
            .filter(is_active=True, is_draft=False)
        )
        groups = ["chat_%s" % id for id in events.values_list("id")]
        groups += [f"user_{self.user.id}"]
        with open("log.txt", "a") as f:
            f.write(f"{self.user} groups: {groups}\n")
        return groups

    @database_sync_to_async
    def get_unread_notifications_count(self):
        return self.user.notifications.filter(read=False).count()
