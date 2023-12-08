from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework import status

from api.permissions import MailIsConfirmed
from api.serializers import EventMarkingSerializer
from api.models import Event


class EventMarkingDetailView(RetrieveAPIView):
    serializer_class = EventMarkingSerializer
    permission_classes = [MailIsConfirmed]

    def get_object(self):
        user = self.request.user

        # все мероприятия, где юзер - орг, не отмечал, начались >= 2 часов назад
        events = Event.objects.filter(
            organizer=user, did_organizer_marking=False
        ).filter_past(hours=2)

        if events.exists():
            return events.first()

        # все мероприятия, где юзер - участник, не отмечался, начались >= 2 часов назад
        events = Event.objects.select_related("participants").filter(
            participants__user=user,
            participants__has_confirmed=False
        ).filter_past(hours=2)

        if events.exists():
            return events.first()

        return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            return Response(status=status.HTTP_200_OK)

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
