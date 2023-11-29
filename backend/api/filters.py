from django_filters import rest_framework as filters
from .models import Event, Category


class CategoryFilters(filters.FilterSet):
    id = filters.MultipleChoiceFilter(field="id")

    class Meta:
        model = Category
        fields = ["id",]


class EventFilters(filters.FilterSet):
    date = filters.DateFilter(method="filter_day_and_time")
    max_age = filters.NumberFilter(field_name="min_age", lookup_expr="lte")
    min_age = filters.NumberFilter(field_name="max_age", lookup_expr="gte")
    category_ids = CategoryFilters()

    def filter_day_and_time(self, queryset, name, value):
        return queryset.filter(**{"day_and_time__date": value})

    class Meta:
        model = Event
        fields = ["day_and_time", "min_age", "max_age", "category"]
