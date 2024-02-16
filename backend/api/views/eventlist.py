import six
import operator
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
)
from elasticsearch_dsl import Q
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import localtime
from django_elasticsearch_dsl.search import Search

from api.serializers import (
    EventDocumentSerializer,
    EventCreateUpdateSerializer,
    FilterQuerySerializer,
)
from api.permissions import StatusPermissions
from api.enums import EventStatus
from api.documents import EventDocument
from api.models import EventFastFilter, EventParticipant
from core.pagination import PageNumberSetPagination


class CustomFilteringFilterBackend(FilteringFilterBackend):
    @classmethod
    def apply_query_in(cls, queryset, options, value):
        __values = cls.split_lookup_complex_multiple_value(value)
        __queries = []
        for __value in __values:
            __queries.append(Q("term", **{options["field"]: __value}))

        if __queries:
            queryset = cls.apply_query(
                queryset=queryset,
                options=options,
                args=[six.moves.reduce(operator.or_, __queries)],
            )

        return queryset


class EventListViewSet(CreateModelMixin, DocumentViewSet):
    document = EventDocument
    pagination_class = PageNumberSetPagination
    serializer_class = {
        "list": EventDocumentSerializer,
        "create": EventCreateUpdateSerializer,
    }

    filter_backends = [
        CompoundSearchFilterBackend,
        CustomFilteringFilterBackend,
    ]

    filter_fields = {
        "country": "country.id",
        "city": "city.id",
        "category": {
            "field": "categories.id",
            "default_lookup": "in",
        },
        "date": "date",
    }

    search_fields = {
        "title": {"fuzziness": "AUTO"},
        "short_description": {"fuzziness": "AUTO"},
    }

    def get_queryset(self):
        qs: Search = super().get_queryset()
        qs = qs.filter(Q("term", is_active=True))
        user = self.request.user
        status = self.request.query_params.get("status")

        if status not in set(EventStatus):
            raise ValidationError(
                "Параметр 'status' не указан или имеет неверное значение. "
                + f"Ожидаемые значения: {[e.value for e in EventStatus]}"
            )

        # "Мои встречи": пользователь является участником/организатором
        if status in [EventStatus.UPCOMING, EventStatus.PAST, EventStatus.DRAFT]:
            qs = qs.filter(Q("term", **{"participants.user.id": user.id}))

        # все события опубликованы, если статус не DRAFT
        qs = qs.filter(Q("term", is_draft=status == EventStatus.DRAFT))

        # PAST включает в себя начавшиеся и прошедшие события, все др. статусы - будущие
        if status == EventStatus.PAST:
            qs = qs.filter(Q("range", start_datetime={"lte": localtime()}))
        else:
            qs = qs.filter(Q("range", start_datetime={"gt": localtime()}))

        # все события гл. страницы фильтруются на наличие свободных мест и открытость
        # если пользователь залогинен, фильтр также учитывает его пол
        if status in [EventStatus.POPULAR, EventStatus.PUBLISHED]:
            gender = user.gender if user.is_authenticated else None
            qs = qs.filter(
                Q(
                    "range",
                    **{f"participants.free_places.{gender or 'total'}": {"gt": 0}},
                )
                & Q("term", is_close_event=False)
            )

        # POPULAR события сортируются по кол-ву свободных мест в сумме
        if status == EventStatus.POPULAR:
            qs = qs.sort("-participants.free_places.total")

        return qs

    def apply_fast_filters(self, queryset):
        query_params = self.request.query_params.dict()
        if "fast_filters" in query_params:
            fast_filters = list(map(int, query_params["fast_filters"].split(",")))
            filter_query = EventFastFilter.objects.get_filter_query(
                fast_filters, self.request.user
            )
            queryset = queryset.filter(filter_query)
        return queryset

    def filter_queryset(self, queryset):
        queryset = self.apply_fast_filters(queryset)
        queryset = super().filter_queryset(queryset)
        min_age = self.request.query_params.get("min_age")
        max_age = self.request.query_params.get("max_age")
        if min_age:
            queryset = queryset.filter(Q("range", **{"max_age": {"gte": min_age}}))
        if max_age:
            queryset = queryset.filter(Q("range", **{"min_age": {"lte": max_age}}))
        return queryset

    def get_permissions(self):
        permission_classes = {
            "list": [StatusPermissions],
            "create": [IsAuthenticated],
        }
        self.permission_classes = permission_classes[self.action]
        return super(EventListViewSet, self).get_permissions()

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response_data = {"events": response.data}
        status = request.query_params.get("status", None)
        user = request.user

        if status == EventStatus.PUBLISHED:
            query_params = self.request.query_params.dict()
            if "category__in" in query_params:
                query_params["category"] = query_params.pop("category__in")
            serializer = FilterQuerySerializer(data=query_params)
            serializer.is_valid(raise_exception=True)
            response_data["filters"] = serializer.data

        if user.is_authenticated:
            unread_notify = user.notifications.filter(read=False).count()
            response_data["unread_notify"] = unread_notify
            response_data["event_rules_applied"] = user.event_rules_applied

        return Response(response_data)

    def perform_create(self, serializer):
        event = serializer.save()
        EventParticipant.objects.create(
            event=event, user=self.request.user, is_organizer=True, has_confirmed=True
        )
