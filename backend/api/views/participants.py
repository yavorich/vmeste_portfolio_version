from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import (
    RetrieveModelMixin,
)
from rest_framework_bulk.mixins import BulkUpdateModelMixin
from rest_framework.generics import GenericAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ParseError, ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils.timezone import localtime, timedelta

from api.permissions import (
    IsEventOrganizer,
    IsEventParticipant,
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
    permission_classes = [IsEventParticipant]

    def get_object(self):
        return get_event_object(self.kwargs["event_pk"])

    def get_queryset(self):
        return self.queryset[self.request.method]

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        event = self.get_object()
        if self.request.method == "PATCH":
            context["participants"] = event.participants.all()
        return context

    def get_permissions(self):
        permission_classes = {
            "GET": [AllowAny],
            "PATCH": [IsEventParticipant],
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
        event = get_event_object(self.kwargs["event_pk"])
        participant = get_object_or_404(event.participants.all(), id=self.kwargs["id"])
        if participant.user == self.request.user:
            raise ValidationError("Event organizer cannot be deleted")
        return participant
