from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import (
    RetrieveModelMixin,
)
from rest_framework_bulk.mixins import BulkUpdateModelMixin, BulkDestroyModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.utils.timezone import localtime, timedelta
from django.shortcuts import get_object_or_404
from typing import Iterable

from apps.api.permissions import (
    IsEventOrganizer,
)
from apps.api.serializers import (
    EventMarkingSerializer,
    EventParticipantsListSerializer,
    EventParticipantBulkSerializer,
)
from apps.api.models import Event, EventParticipant


class EventMarkingDetailView(RetrieveAPIView):
    serializer_class = EventMarkingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        # все мероприятия, где юзер - участник и не отмечался
        # или юзер - орг и не отмечал
        # начались >= 2 часов назад
        participance = EventParticipant.objects.filter(
            Q(is_organizer=True, event__did_organizer_marking=False)
            | Q(has_confirmed=False),
            user=user,
            event__start_datetime__lte=localtime() - timedelta(hours=2),
        )
        if participance.exists():
            return participance.first().event

        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventParticipantView(
    RetrieveModelMixin, BulkUpdateModelMixin, BulkDestroyModelMixin, GenericAPIView
):
    def get_object(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], is_active=True)

    def get_queryset(self):
        if self.request.method == "GET":
            return Event.objects.all()

        event = self.get_object()
        return event.participants.filter(is_organizer=False)

    def filter_queryset(self, queryset):
        ids = [e["id"] for e in self.request.data]
        return queryset.filter(id__in=ids)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return EventParticipantsListSerializer
        return EventParticipantBulkSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        event = self.get_object()
        if self.request.method in ["PATCH"]:
            context["participants"] = event.participants.all()
        return context

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsEventOrganizer]
        return super(EventParticipantView, self).get_permissions()

    def confirm_marking(self):
        event = self.get_object()
        event.did_organizer_marking = True
        event.save()

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().partial_bulk_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        self.perform_bulk_destroy(qs)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        serializer.save()
        self.confirm_marking()

    def perform_bulk_destroy(self, objects: Iterable[EventParticipant]):
        for obj in objects:
            obj.kicked_by_organizer = True
            obj.save()
