from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)

from api.models import Event
from api.serializers import EventDetailSerializer, EventCreateUpdateSerializer
from api.permissions import IsEventOrganizer
from api.services import get_event_object


class EventDetailViewSet(
    RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet
):
    queryset = Event.objects.all()
    serializer_class = {
        "retrieve": EventDetailSerializer,
        "partial_update": EventCreateUpdateSerializer,
    }

    def get_object(self):
        return get_event_object(self.kwargs["event_pk"])

    def get_permissions(self):
        permission_classes = {
            "retrieve": [AllowAny],
            "partial_update": [IsEventOrganizer],
            "destroy": [IsEventOrganizer],
        }
        self.permission_classes = permission_classes[self.action]
        return super(EventDetailViewSet, self).get_permissions()

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        if self.request.user.is_authenticated:
            unread_notify = self.request.user.notifications.filter(read=False).count()
            data["unread_notify"] = unread_notify
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
