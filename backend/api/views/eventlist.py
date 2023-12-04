from rest_framework import generics
from rest_framework.response import Response
from api.models import Event, Theme, Notification
from api.serializers import EventSerializer, ThemeSerializer
from api.permissions import StatusPermissions
from api.enums import EventStatus
from api.filters import EventFilters


class EventListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [StatusPermissions]
    filterset_class = EventFilters
    queryset = Event.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        status = self.request.query_params.get("status")
        is_auth = self.request.user.is_authenticated

        if status != EventStatus.POPULAR and is_auth:
            context["user"] = self.request.user

        return context

    def get_filters_data(self, request):
        filterset = self.filterset_class(request.GET)
        data = filterset.data.copy()
        exclude_keys = ["city", "country", "category"]

        if "max_age" in data:
            data["max_age"] = int(data["max_age"])
        if "min_age" in data:
            data["min_age"] = int(data["min_age"])

        if "category" in data:
            category = data["category"]
            categories = list(map(int, category.split(",")))
            filtered_themes = Theme.objects.filter(
                categories__id__in=categories
            ).distinct()
            data["themes"] = ThemeSerializer(
                filtered_themes, many=True, context={"categories": categories}
            ).data

        cleaned_data = {k: data[k] for k in data.keys() if k not in exclude_keys}
        return cleaned_data

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response_data = {"events": response.data}
        status = request.query_params.get("status", None)

        if status == EventStatus.PUBLISHED:
            response_data["filters"] = self.get_filters_data(request)

        if self.request.user.is_authenticated:
            unread_notify = Notification.objects.filter(
                user=self.request.user, read=False
            ).count()
            response_data["unread_notify"] = unread_notify

        return Response(response_data)
