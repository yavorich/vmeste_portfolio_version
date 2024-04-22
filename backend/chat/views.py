from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from itertools import groupby

from api.models import Event
from api.permissions import IsEventParticipant
from api.enums import EventStatus
from chat.serializers import (
    ChatListSerializer,
    ChatEventSerializer,
    MessageSerializer,
    MessageSendSerializer,
)
from chat.models import Message, Chat, ReadMessage
from chat.utils import send_ws_message
from core.pagination import PageNumberSetPagination


class ChatListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatListSerializer
    pagination_class = PageNumberSetPagination

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
        return Message.objects.filter(chat__event=self.kwargs["event_pk"]).order_by(
            "sent_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def read_all_messages(self, messages):
        for message in messages:
            ReadMessage.objects.get_or_create(user=self.request.user, message=message)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], is_active=True)
        event_serializer = ChatEventSerializer(event, context={"request": request})
        grouped_messages = []
        for date, messages in groupby(
            queryset, lambda m: m.sent_at.astimezone(tz=localtime().tzinfo).date()
        ):
            messages_queryset = Message.objects.filter(id__in=[m.id for m in messages])
            page = self.paginate_queryset(messages_queryset)
            if page is not None and "page" in request.query_params:
                serializer = self.get_serializer(
                    page, many=True, context=self.get_serializer_context()
                )
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(
                    messages_queryset, many=True, context=self.get_serializer_context()
                )
                response = Response({"results": serializer.data})
            grouped_messages.append({"date": date, **response.data})

        self.read_all_messages(queryset)
        return Response({"event": event_serializer.data, "messages": grouped_messages})


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
