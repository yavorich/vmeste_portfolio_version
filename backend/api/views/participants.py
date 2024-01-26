from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import (
    RetrieveModelMixin,
)
from rest_framework_bulk.mixins import BulkUpdateModelMixin
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ParseError
from django.shortcuts import get_object_or_404

from api.permissions import (
    IsEventOrganizer,
    IsEventOrganizerOrParticipant,
)
from api.serializers import (
    EventMarkingSerializer,
    EventRetrieveParticipantsSerializer,
    EventParticipantBulkUpdateSerializer,
    EventParticipantDeleteSerializer,
)
from api.models import Event, EventParticipant
from api.services import get_event_object


class EventMarkingDetailView(RetrieveAPIView):
    serializer_class = EventMarkingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        # все мероприятия, где юзер - орг, не отмечал, начались >= 2 часов назад
        events = Event.objects.filter(
            organizer=user,
            did_organizer_marking=False,
            is_active=True,
            is_draft=False,
        ).filter_past(hours=2)

        if events.exists():
            return events.first()

        # все мероприятия, где юзер - участник, не отмечался, начались >= 2 часов назад
        events = (
            Event.objects.select_related("participants")
            .filter(participants__user=user, participants__has_confirmed=False)
            .filter_past(hours=2)
        )

        if events.exists():
            return events.first()

        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventParticipantRetrieveUpdateView(
    RetrieveModelMixin, BulkUpdateModelMixin, GenericAPIView
):
    queryset = {
        "GET": Event.objects.all(),
        "PATCH": EventParticipant.objects.all(),
    }
    serializer_class = {
        "GET": EventRetrieveParticipantsSerializer,
        "PATCH": EventParticipantBulkUpdateSerializer,
    }
    permission_classes = [IsEventOrganizerOrParticipant]

    def get_object(self):
        return get_event_object(self.kwargs["event_pk"])

    def get_queryset(self):
        return self.queryset[self.request.method]

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def get_permissions(self):
        permission_classes = {
            "GET": [AllowAny],
            "PATCH": [IsEventOrganizerOrParticipant],
        }
        self.permission_classes = permission_classes[self.request.method]
        return super(EventParticipantRetrieveUpdateView, self).get_permissions()

    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if not data or not isinstance(data, list):
            raise ParseError("Body is empty or not valid")
        perm = IsEventOrganizer()
        if not perm.has_permission(self.request, self) and (
            user.id != data[0]["id"] or len(data) > 1
        ):
            raise PermissionDenied("User is not an event organizer")
        return super().partial_bulk_update(request, *args, **kwargs)


class EventParticipantDeleteView(DestroyAPIView):
    queryset = EventParticipant.objects.all()
    serializer_class = EventParticipantDeleteSerializer
    permission_classes = [IsEventOrganizer]

    def get_object(self):
        return get_object_or_404(EventParticipant, id=self.kwargs["id"])
