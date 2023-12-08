from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from django.shortcuts import get_object_or_404

from api.models import Event, Notification
from api.serializers import EventDetailSerializer, EventCreateUpdateSerializer
from api.permissions import MailIsConfirmed


class EventDetailViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Event.objects.all()
    permission_classes = {"retrieve": [AllowAny], "partial_update": [MailIsConfirmed]}
    serializer_class = {
        "retrieve": EventDetailSerializer,
        "partial_update": EventCreateUpdateSerializer,
    }

    def get_object(self):
        pk = self.kwargs["pk"]
        if pk.isdigit():
            return get_object_or_404(Event, pk=pk)
        return get_object_or_404(Event, uuid=pk)

    def get_permissions(self):
        self.permission_classes = self.permission_classes[self.action]
        return super(EventDetailViewSet, self).get_permissions()

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.request.user.is_authenticated:
            context["user"] = self.request.user
        return context

    def retrieve(self, request, *args, **kwargs):
        data = super().retrieve(request, *args, **kwargs).data
        if self.request.user.is_authenticated:
            unread_notify = Notification.objects.filter(
                user=self.request.user, read=False
            ).count()
            data["unread_notify"] = unread_notify
        return Response(data)
