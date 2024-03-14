from rest_framework_bulk.mixins import BulkCreateModelMixin
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from api.permissions import (
    IsEventParticipant,
    IsMediaTimeValid,
)
from api.serializers import EventMediaBulkCreateSerializer, EventMediaListSerializer
from api.models import Event, EventMedia
from core.pagination import PageNumberSetPagination


class EventMediaViewSet(
    BulkCreateModelMixin, RetrieveAPIView, ListAPIView, GenericViewSet
):
    permission_classes = [
        IsEventParticipant,
        IsMediaTimeValid,
    ]
    serializer_class = {
        "GET": EventMediaListSerializer,
        "POST": EventMediaBulkCreateSerializer,
    }
    pagination_class = PageNumberSetPagination
    queryset = EventMedia.objects.all()

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"], is_active=True)
        return self.queryset.filter(event=event)

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs[self.lookup_field])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["event"] = get_object_or_404(
            Event, pk=self.kwargs["event_pk"], is_active=True
        )
        context["user"] = self.request.user
        return context

    def get_serializer_class(self):
        return self.serializer_class[self.request.method]

    def get_request_data(self):
        return [{"file": e} for e in self.request.data.getlist("files")]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.get_request_data(), many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
