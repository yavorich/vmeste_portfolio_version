from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from apps.api.models import Event, EventParticipant, User
from apps.api.serializers import EventParticipantTicketSerializer, UserShortSerializer
from apps.api.permissions import IsEventOrganizerOrScanner


class EventParticipantTicketView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = EventParticipantTicketSerializer

    def get_object(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], is_active=True)
        return get_object_or_404(EventParticipant, event=event, user=self.request.user)


class EventTicketScanView(APIView):
    permission_classes = [IsEventOrganizerOrScanner]

    def get_object(self, ticket_id):
        return get_object_or_404(
            EventParticipant, pk=ticket_id, event_id=self.kwargs["event_pk"]
        )

    def post(self, request, *args, **kwargs):
        ticket_id = request.data.get("ticket_id")
        if not ticket_id:
            raise ValidationError({"error": "Некорректный QR-код"})

        participant = self.get_object(ticket_id)
        if participant.qr_code_verified:  # предотвращение повторного сканирования
            raise ValidationError({"error": "Повторное сканирование"})

        participant.qr_code_verified = True
        participant.save(update_fields=["qr_code_verified"])

        return Response({"success": f"Билет {ticket_id} подтверждён"})


class ScannerAccountListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserShortSerializer

    def get_queryset(self):
        return User.objects.filter(
            is_active=True, is_registered=True, is_deleted=False, is_staff=False
        ).exclude(pk=self.request.user.pk)
