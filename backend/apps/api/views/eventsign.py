from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.api.models import Event
from apps.api.serializers import (
    EventSignSerializer,
    EventCancelSerializer,
    EventReportSerializer,
    EventConfirmSerializer,
)


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
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def cancel(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def report(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def confirm(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
