from rest_framework_bulk.mixins import BulkCreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import GenericViewSet

from api.permissions import (
    MailIsConfirmed,
    IsEventOrganizerOrParticipant,
    IsMediaTimeValid,
)
from api.serializers import EventMediaBulkCreateSerializer, EventMediaListSerializer
from api.models import EventMedia
from api.services import get_event_object
from core.pagination import PageNumberSetPagination


class EventMediaViewSet(
    BulkCreateModelMixin, RetrieveAPIView, ListAPIView, GenericViewSet
):
    permission_classes = [
        MailIsConfirmed,
        IsEventOrganizerOrParticipant,
        IsMediaTimeValid,
    ]
    serializer_class = {
        "GET": EventMediaListSerializer,
        "POST": EventMediaBulkCreateSerializer,
    }
    pagination_class = PageNumberSetPagination
    queryset = EventMedia.objects.all()

    def get_queryset(self):
        event = get_event_object(self.kwargs["event_pk"])
        return self.queryset.filter(event=event)

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs[self.lookup_field])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["event"] = get_event_object(self.kwargs["event_pk"])
        context["user"] = self.request.user
        return context

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
