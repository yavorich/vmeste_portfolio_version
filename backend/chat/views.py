from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import ValidationError
from django.db.models import Q

from api.models import Event
from api.permissions import MailIsConfirmed, IsEventOrganizerOrParticipant
from api.enums import EventStatus
from chat.serializers import (
    ChatListSerializer,
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

        queryset = Event.objects.filter_organizer_or_participant(user)
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
    serializer_class = MessageSerializer
    pagination_class = PageNumberSetPagination

    def get_queryset(self):
        return Message.objects.filter(chat__event=self.kwargs["event_id"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context


class MessageSendView(CreateAPIView):
    permission_classes = [MailIsConfirmed, IsEventOrganizerOrParticipant]
    serializer_class = MessageSendSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["chat"] = Chat.objects.get(event__id=self.kwargs["event_id"])
        context["sender"] = self.request.user
        context["is_info"] = False
        return context

    def perform_create(self, serializer: MessageSendSerializer):
        serializer.save()
        message = serializer.data
        event_id = self.kwargs["event_id"]
        send_ws_message(message, event_id)
