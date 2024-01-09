from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import ValidationError
from itertools import groupby

from api.models import Event
from api.permissions import MailIsConfirmed, IsEventOrganizerOrParticipant
from api.services import get_event_object
from api.enums import EventStatus
from chat.serializers import (
    ChatListSerializer,
    ChatEventSerializer,
    MessageSerializer,
    MessageSendSerializer,
)
from chat.models import Message, Chat
from chat.utils import send_ws_message
from core.pagination import PageNumberSetPagination


class ChatListView(ListAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = ChatListSerializer
    pagination_class = PageNumberSetPagination

    def get_queryset(self):
        status = self.request.query_params.get("status")
        user = self.request.user

        if status not in [EventStatus.UPCOMING, EventStatus.PAST]:
            raise ValidationError("Status query parameter is required (upcoming/past)")

        queryset = Event.objects.filter_organizer_or_participant(user).distinct()
        queryset = getattr(queryset, f"filter_{status}")()
        return queryset

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
    permission_classes = [MailIsConfirmed, IsEventOrganizerOrParticipant]
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

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        event = get_event_object(self.kwargs["event_pk"])
        event_serializer = ChatEventSerializer(event)
        grouped_messages = []
        for date, messages in groupby(queryset, lambda m: m.sent_at.date()):
            messages_queryset = Message.objects.filter(id__in=[m.id for m in messages])
            page = self.paginate_queryset(messages_queryset)
            if page is not None:
                serializer = self.get_serializer(
                    page, many=True, context=self.get_serializer_context()
                )
                response = self.get_paginated_response(serializer.data)
            else:
                serializer = self.get_serializer(
                    messages_queryset, context=self.get_serializer_context()
                )
                response = Response(serializer.data)
            grouped_messages.append({"date": date, **response.data})

        return Response({"event": event_serializer.data, "messages": grouped_messages})


class MessageSendView(CreateAPIView):
    permission_classes = [MailIsConfirmed, IsEventOrganizerOrParticipant]
    serializer_class = MessageSendSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["chat"] = Chat.objects.get(event__id=self.kwargs["event_pk"])
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
