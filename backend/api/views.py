from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.timezone import now
from django.db import models
from .models import Event
from . import serializers
from .permissions import StatusPermissions
from .enums import EventStatus
from .filters import EventFilters


class EventListView(generics.ListAPIView):
    serializer_class = serializers.EventSerializer
    permission_classes = [StatusPermissions]
    filterset_class = EventFilters
    queryset = Event.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get("status", None)
        if status:
            queryset = queryset.filter(published=status != EventStatus.DRAFT)
            if status == EventStatus.PUBLISHED:
                queryset = queryset.filter(location__isnull=False)
            if status == EventStatus.PAST:
                queryset = queryset.filter(day_and_time__lte=now())
            else:
                queryset = queryset.filter(day_and_time__gt=now())
            if status == EventStatus.POPULAR:
                queryset = queryset.annotate(
                    total_participants=models.Count("participants"),
                ).order_by("-total_participants")
            elif self.request.user.is_authenticated:
                queryset = queryset.filter(
                    participants__profile__user=self.request.user
                )
        filterset = self.filterset_class(self.request.GET, queryset=queryset)
        return filterset.qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        filterset = self.filterset_class(request.GET)
        serializer = self.get_serializer(queryset, many=True)
        response_data = {"results": serializer.data}
        if request.query_params.get("status", None) == EventStatus.PUBLISHED:
            response_data["filters"] = filterset.data
        return Response(response_data)
