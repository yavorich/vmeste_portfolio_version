from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from apps.api.models import Event
from apps.api.serializers import (
    EventSignSerializer,
    EventCancelSerializer,
    EventReportSerializer,
    EventConfirmSerializer,
)
from apps.api.services.payment import do_payment_on_sign


class EventPublishedViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = {
        "sign": EventSignSerializer,
        "cancel": EventCancelSerializer,
        "report": EventReportSerializer,
        "confirm": EventConfirmSerializer,
    }
    queryset = Event.objects.all()

    def get_object(self):
        return get_object_or_404(Event, pk=self.kwargs["pk"], is_active=True)

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(detail=True, methods=["post"])
    def sign(self, request, *args, **kwargs):
        self.update(request, *args, **kwargs)
        event = self.get_object()
        payment_data = do_payment_on_sign(event, request)
        return Response(payment_data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def report(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def confirm(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
