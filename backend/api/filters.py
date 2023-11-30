from django_filters import rest_framework as filters
from django.db.models import Count
from django.utils.timezone import now
from .models import Event
from .enums import EventStatus


class ListFilter(filters.Filter):
    def filter(self, qs, value):
        if not value:
            return qs
        self.lookup_expr = 'in'
        values = value.split(',')
        return super(ListFilter, self).filter(qs, values)


class EventFilters(filters.FilterSet):
    date = filters.DateFilter(method="filter_day_and_time")
    max_age = filters.NumberFilter(field_name="min_age", lookup_expr="lte")
    min_age = filters.NumberFilter(field_name="max_age", lookup_expr="gte")
    country = ListFilter(field_name="country__id")
    city = ListFilter(field_name="city__id")
    category = ListFilter(field_name="category__id")
    status = filters.CharFilter(method="filter_status")

    def filter_day_and_time(self, qs, name, value):
        return qs.filter(**{"day_and_time__date": value})

    def filter_status(self, qs, name, value):
        qs = qs.filter(published=value != EventStatus.DRAFT)
        if value == EventStatus.PUBLISHED:
            qs = qs.filter(
                location__isnull=False).order_by("-day_and_time")
        if value == EventStatus.PAST:
            qs = qs.filter(day_and_time__lte=now())
        else:
            qs = qs.filter(day_and_time__gt=now())
        if value == EventStatus.POPULAR:
            qs = qs.annotate(
                total_participants=Count("participants"),
            ).order_by("-total_participants")
        if value not in [EventStatus.POPULAR, EventStatus.PUBLISHED]:
            qs = qs.filter(
                participants__profile__user=self.request.user)
        return qs

    class Meta:
        model = Event
        fields = ["day_and_time", "min_age", "max_age",
                  "country", "city", "category"]
