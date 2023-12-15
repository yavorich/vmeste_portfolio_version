from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from api.models import Event
from api.permissions import MailIsConfirmed
from chat.serializers import (
    ChatListSerializer,
    MessageSerializer,
    MessageSendSerializer,
)
from chat.models import Message
from chat.utils import send_ws_message

import logging

logger = logging.getLogger("ws")


class ChatListView(ListAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = ChatListSerializer

    def get_queryset(self):
        return Event.objects.filter(participants__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        chats = super().list(request, *args, **kwargs).data
        unread_notify = request.user.notifications.filter(read=False).count()
        return Response(
            data={"unread_notify": unread_notify, "chats": chats}, status=HTTP_200_OK
        )


class MessageListView(ListAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(event=self.kwargs["event_id"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


class MessageSendView(CreateAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = MessageSendSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["event"] = Event.objects.get(id=self.kwargs["event_id"])
        context["sender"] = self.request.user
        context["is_info"] = False
        return context

    def perform_create(self, serializer: MessageSendSerializer):
        serializer.save()
        message = serializer.data
        event_id = self.kwargs["event_id"]
        logger.debug("Sending ws message...")
        send_ws_message(message, event_id)
