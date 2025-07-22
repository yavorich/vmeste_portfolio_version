import six
import operator
from itertools import groupby

from django.core.management import call_command
from django_elasticsearch_dsl.search import Search
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
)
from django.utils.timezone import localtime, timedelta
from elasticsearch_dsl import Q
from elasticsearch.exceptions import NotFoundError
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from apps.api.serializers import (
    EventDocumentSerializer,
    EventCreateUpdateSerializer,
    FilterQuerySerializer,
)
from apps.api.permissions import StatusPermissions
from apps.api.enums import EventStatus
from apps.api.documents import EventDocument
from apps.api.models import EventFastFilter
from apps.api.serializers.event import EventDocumentFullImageSerializer
from apps.api.services.payment import do_payment_on_create
from core.pagination import PageNumberSetPagination
from core.utils import humanize_date


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

    @staticmethod
    def apply_fast_filters(request, queryset):
        query_params = request.query_params.dict()
        if "fast_filters" in query_params:
            fast_filters = list(map(int, query_params["fast_filters"].split(",")))
            filter_query = EventFastFilter.objects.get_filter_query(
                fast_filters, request.user
            )
            queryset = queryset.filter(filter_query)
        return queryset

    @staticmethod
    def apply_status_filter(request, queryset):
        qs: Search = queryset.filter(Q("term", is_active=True))
        user = request.user
        status = request.query_params.get("status")
        search = request.query_params.get("search")

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

        # PAST включает в себя начавшиеся и прошедшие события
        if status == EventStatus.PAST:
            qs = qs.filter(Q("range", start_datetime={"lte": localtime()}))
        elif status != EventStatus.DRAFT:  # все др. статусы - будущие, кроме DRAFT
            qs = qs.filter(Q("range", start_datetime={"gt": localtime()}))

        # все события гл. страницы фильтруются на наличие свободных мест и открытость
        # если пользователь залогинен, фильтр также учитывает его пол
        if status in [EventStatus.POPULAR, EventStatus.PUBLISHED]:
            qs = qs.filter(Q("term", is_close_event=False))

        # сортировка событий в зависимости от статуса
        if not search:
            if status == EventStatus.PAST:
                qs = qs.sort("-start_datetime")
            elif status == EventStatus.POPULAR:
                qs = qs.sort("-participants.free_places.total")
            else:
                qs = qs.sort("start_datetime")

        total = qs.count()
        return qs[:total]

    @staticmethod
    def apply_age_filter(request, queryset):
        min_age = request.query_params.get("min_age")
        max_age = request.query_params.get("max_age")
        if min_age:
            queryset = queryset.filter(Q("range", **{"max_age": {"gte": min_age}}))
        if max_age:
            queryset = queryset.filter(Q("range", **{"min_age": {"lte": max_age}}))
        return queryset

    def filter_queryset(self, request, queryset, view):
        try:
            queryset = super().filter_queryset(request, queryset, view)
            queryset = self.apply_status_filter(request, queryset)
            queryset = self.apply_fast_filters(request, queryset)
            queryset = self.apply_age_filter(request, queryset)
            return queryset
        except NotFoundError:
            call_command("search_index", "--rebuild", "-f")
            return self.filter_queryset(request, queryset, view)


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

    search_fields = ("title", "short_description")

    def get_queryset(self):
        return super().get_queryset().filter("term", is_active=True)

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

    def _list_queryset(self, request, queryset):
        page = self.paginate_queryset(queryset)
        if page is not None and "page" in request.query_params:
            serializer = self.get_serializer(
                page, many=True, context=self.get_serializer_context()
            )
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(
                queryset, many=True, context=self.get_serializer_context()
            )
            response = Response({"results": serializer.data})
        return response

    def _list_published(self, request):
        queryset: Search = self.filter_queryset(self.get_queryset())

        # Разделение на ближайшие и более поздние
        next_week = localtime().date() + timedelta(days=7)
        soon = queryset.filter(Q("range", date={"lt": next_week}))
        later = queryset.filter(Q("range", date={"gte": next_week}))

        # Группировка ближайших событий по дням
        grouped_events = []
        for date, events in groupby(soon, lambda e: e.date):
            ids = [e.id for e in events]
            events_queryset = queryset.filter("terms", id=ids)
            response = self._list_queryset(request, events_queryset)
            grouped_events.append({"date": humanize_date(date), **response.data})

        # Добавление более поздних событий
        response = self._list_queryset(request, later)
        if len(response.data["results"]) != 0:
            grouped_events.append({"date": "Позже", **response.data})

        response_data = {"events": grouped_events}

        # Добавление информации о фильтрах
        query_params = self.request.query_params.dict()
        if "category__in" in query_params:
            query_params["category"] = query_params.pop("category__in")
        serializer = FilterQuerySerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        response_data["filters"] = serializer.data
        return response_data

    def _list_popular(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EventDocumentFullImageSerializer(
                page, many=True, context=self.get_serializer_context()
            )
            return {"events": self.get_paginated_response(serializer.data).data}

        serializer = EventDocumentFullImageSerializer(
            queryset, many=True, context=self.get_serializer_context()
        )
        return {"events": serializer.data}

    def list(self, request, *args, **kwargs):
        status = request.query_params.get("status", None)
        if status == EventStatus.PUBLISHED:
            response_data = self._list_published(request)
        elif status == EventStatus.POPULAR:
            response_data = self._list_popular(request)
        else:
            response = super().list(request, *args, **kwargs)
            response_data = {"events": response.data}

        # Добавление прочих данных для аутентифицированных пользователей
        user = request.user
        if user.is_authenticated:
            unread_notify = user.notifications.filter(read=False).count()
            response_data["unread_notify"] = unread_notify
            response_data["event_rules_applied"] = user.event_rules_applied

        return Response(response_data)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        payment_data = do_payment_on_create(instance, request)
        headers = self.get_success_headers(serializer.data)
        return Response({**serializer.data, **payment_data}, status=status.HTTP_201_CREATED, headers=headers)
