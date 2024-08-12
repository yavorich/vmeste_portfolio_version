from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.api.models import EventFastFilter
from apps.api.serializers import EventFastFilterSerializer


class EventFastFiltersListView(ListAPIView):
    queryset = EventFastFilter.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    serializer_class = EventFastFilterSerializer
