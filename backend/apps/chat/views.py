from django.db.models import OuterRef, Exists
from django.utils.timezone import localtime
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from itertools import groupby

from apps.admin_history.models import HistoryLog, ActionFlag
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
from apps.chat.utils import send_ws_message, send_ws_unread_messages
from core.pagination import PageNumberSetPagination


class ChatEventViewSet(ReadOnlyModelViewSet):
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

    def get_object(self):
        return get_object_or_404(
            Event.objects.filter_participant(self.request.user)
            .distinct()
            .filter(is_draft=False, is_active=True),
            pk=self.kwargs["pk"],
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
        user = self.request.user

        unread_messages_query = messages.annotate(
            is_read=Exists(
                ReadMessage.objects.filter(user=user, message_id=OuterRef("pk"))
            )
        ).filter(is_read=False)
        unread_messages = list(unread_messages_query.iterator())
        ReadMessage.objects.bulk_create(
            [ReadMessage(user=user, message=message) for message in unread_messages]
        )
        send_ws_unread_messages(user)
        HistoryLog.objects.log_actions(
            user_id=user.pk,
            queryset=unread_messages,
            action_flag=ActionFlag.CHANGE,
            change_message=[{"changed": {"fields": ["Прочитано"]}}],
            is_admin=False,
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
        HistoryLog.objects.log_actions(
            user_id=self.request.user.pk,
            queryset=[message],
            action_flag=ActionFlag.ADDITION,
            change_message=[{"added": {}}],
            is_admin=False,
        )
