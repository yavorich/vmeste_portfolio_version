from django_filters import rest_framework as filters
from django.db.models import Count
from django.utils.timezone import now

from api.models import Event
from api.enums import EventStatus
from .list import ListFilter


class EventFilters(filters.FilterSet):
    date = filters.DateFilter(method="filter_date")
    max_age = filters.NumberFilter(field_name="min_age", lookup_expr="lte")
    min_age = filters.NumberFilter(field_name="max_age", lookup_expr="gte")
    country = ListFilter(field_name="country__id")
    city = ListFilter(field_name="city__id")
    category = ListFilter(field_name="category__id")
    status = filters.CharFilter(method="filter_status")

    def filter_date(self, qs, name, value):
        return qs.filter(**{"start_datetime__date": value})

    def filter_status(self, qs, name, value):
        qs = qs.filter(published=value != EventStatus.DRAFT)
        if value == EventStatus.PUBLISHED:
            qs = qs.filter(location__isnull=False).order_by("-start_datetime")
        if value == EventStatus.PAST:
            qs = qs.filter(start_datetime__lte=now())
        else:
            qs = qs.filter(start_datetime__gt=now())
        if value == EventStatus.POPULAR:
            qs = qs.annotate(
                total_participants=Count("participants"),
            ).order_by("-total_participants")
        if value not in [EventStatus.POPULAR, EventStatus.PUBLISHED]:
            qs = qs.filter(participants__user=self.request.user)
        return qs

    class Meta:
        model = Event
        fields = ["start_datetime", "min_age", "max_age", "country", "city", "category"]
