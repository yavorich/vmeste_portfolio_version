from django_filters import rest_framework as filters

from api.models import Event
from api.enums import EventStatus
from .list import ListFilter


class EventFilters(filters.FilterSet):
    date = filters.DateFilter()
    max_age = filters.NumberFilter(field_name="min_age", lookup_expr="lte")
    min_age = filters.NumberFilter(field_name="max_age", lookup_expr="gte")
    country = ListFilter(field_name="country__id")
    city = ListFilter(field_name="city__id")
    category = filters.Filter(field_name="categories", method="filter_category")
    status = filters.CharFilter(method="filter_status", required=True)

    def filter_category(self, qs, name, value):
        values = value.split(",")
        return qs.filter(categories__in=values)

    def filter_status(self, qs, name, value):
        user = self.request.user

        # "Мои встречи": пользователь является участником/организатором
        if value in [EventStatus.UPCOMING, EventStatus.PAST, EventStatus.DRAFT]:
            qs = qs.filter_organizer_or_participant(user)

        # все события опубликованы, если статус не DRAFT
        qs = qs.filter(is_draft=value == EventStatus.DRAFT)

        # PAST включает в себя начавшиеся и прошедшие события, все др. статусы - будущие
        if value == EventStatus.PAST:
            qs = qs.filter_past()
        else:
            qs = qs.filter_upcoming()

        # все события гл. страницы фильтруются на наличие свободных мест и открытость
        # если пользователь залогинен, фильтр также учитывает его пол
        if value in [EventStatus.POPULAR, EventStatus.PUBLISHED]:
            gender = user.gender if user.is_authenticated else None
            qs = qs.filter(is_close_event=False).filter_has_free_places(gender)

        # POPULAR события сортируются по кол-ву свободных мест в сумме
        if value == EventStatus.POPULAR:
            qs = qs.order_by("free_places")

        return qs

    class Meta:
        model = Event
        fields = ["date", "min_age", "max_age", "country", "city", "categories"]
