from rest_framework_bulk.mixins import BulkCreateModelMixin
from rest_framework.generics import ListAPIView

from api.permissions import MailIsConfirmed
from api.serializers import EventMediaBulkCreateSerializer
from api.models import EventMedia
from api.services import get_event_object


class EventMediaListCreateView(BulkCreateModelMixin, ListAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = EventMediaBulkCreateSerializer
    queryset = EventMedia.objects.all()

    def get_queryset(self):
        event = get_event_object(self.kwargs["pk"])
        return self.queryset.filter(event=event)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["event"] = get_event_object(self.kwargs["pk"])
        return context

    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
