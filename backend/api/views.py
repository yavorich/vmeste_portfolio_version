from rest_framework import generics
from rest_framework.response import Response
from .models import Event, Theme
from . import serializers
from .permissions import StatusPermissions
from .enums import EventStatus
from .filters import EventFilters


class EventListView(generics.ListAPIView):
    serializer_class = serializers.EventSerializer
    permission_classes = [StatusPermissions]
    filterset_class = EventFilters
    queryset = Event.objects.all()

    def get_filters_data(self, request):
        filterset = self.filterset_class(request.GET)
        data = filterset.data.copy()
        exclude_keys = ["city", "country", "category"]

        data["max_age"] = int(data["max_age"])
        data["min_age"] = int(data["min_age"])

        if "category" in data:
            category = data["category"]
            categories = list(map(int, category.split(',')))
            filtered_themes = Theme.objects.filter(
                categories__id__in=categories).distinct()
            data["themes"] = serializers.ThemeSerializer(
                filtered_themes, many=True,
                context={"categories": categories}).data

        cleaned_data = {k: data[k] for k in data.keys()
                        if k not in exclude_keys}
        return cleaned_data

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response_data = {"events": response.data}
        if request.query_params.get("status", None) == EventStatus.PUBLISHED:
            response_data["filters"] = self.get_filters_data(request)
        return Response(response_data)
