from rest_framework_bulk.mixins import BulkCreateModelMixin
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin

from api.permissions import MailIsConfirmed
from api.serializers import EventMediaBulkCreateSerializer
from api.models import EventMedia
from api.services import get_event_object


class EventMediaListCreateView(ListModelMixin, BulkCreateModelMixin, GenericAPIView):
    permission_classes = [MailIsConfirmed]
    serializer_class = EventMediaBulkCreateSerializer
    queryset = EventMedia.objects.all()

    def get_queryset(self):
        event = get_event_object(self.kwargs["pk"])
        return self.queryset.filter(event=event)
