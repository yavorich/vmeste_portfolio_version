from django.db.models import OuterRef, Exists
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from itertools import groupby

from apps.api.models import Event
from apps.api.permissions import IsEventParticipant
from apps.api.enums import EventStatus
from apps.chat.serializers import (
    ChatListSerializer,
    ChatEventSerializer,
    MessageSerializer,
    MessageSendSerializer,
)
from apps.chat.models import Message, Chat, ReadMessage
from apps.chat.utils import send_ws_message
from core.pagination import PageNumberSetPagination


class ChatListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatListSerializer

    def get_queryset(self):
        status = self.request.query_params.get("status")
        user = self.request.user

        if status not in [EventStatus.UPCOMING, EventStatus.PAST]:
            raise ValidationError("Status query parameter is required (upcoming/past)")

        queryset = (
            Event.objects.filter_participant(user)
            .distinct()
            .filter(is_draft=False, is_active=True)
        )
        queryset = getattr(queryset, f"filter_{status}")()
        return sorted(
            queryset, key=lambda x: x.chat.messages.latest().sent_at, reverse=True
        )

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
    permission_classes = [IsAuthenticated, IsEventParticipant]
    pagination_class = PageNumberSetPagination
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.filter(chat__event=self.kwargs["event_pk"]).order_by(
            "-sent_at"
        )
        self.read_all_messages(queryset)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def read_all_messages(self, messages):
        ReadMessage.objects.bulk_create(
            [
                ReadMessage(user=self.request.user, message_id=message_id)
                for message_id in messages.annotate(
                    is_read=Exists(
                        ReadMessage.objects.filter(
                            user=self.request.user, message_id=OuterRef("pk")
                        )
                    )
                )
                .filter(is_read=False)
                .values_list("pk", flat=True)
            ]
        )


class MessageSendView(CreateAPIView):
    permission_classes = [IsAuthenticated, IsEventParticipant]
    serializer_class = MessageSendSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["chat"] = Chat.objects.get(pk=self.kwargs["event_pk"])
        context["sender"] = self.request.user
        context["is_info"] = False
        context["is_incoming"] = False
        return context

    def perform_create(self, serializer: MessageSendSerializer):
        message = serializer.save()
        message_serializer = MessageSerializer(
            instance=message, context={"user": self.request.user}
        )
        event_pk = self.kwargs["event_pk"]
        send_ws_message(message_serializer.data, event_pk)
