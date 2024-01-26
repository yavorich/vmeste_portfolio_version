from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from api.models import EventFastFilter
from api.serializers import EventFastFilterSerializer


class EventFastFiltersListView(ListAPIView):
    queryset = EventFastFilter.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    serializer_class = EventFastFilterSerializer
