from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
)
from elasticsearch_dsl import Q
from rest_framework.exceptions import ValidationError
from django.utils.timezone import now
from django_elasticsearch_dsl.search import Search

from api.serializers import (
    EventDocumentSerializer,
    EventCreateUpdateSerializer,
    FilterQuerySerializer,
)
from api.permissions import StatusPermissions, MailIsConfirmed
from api.enums import EventStatus
from api.documents import EventDocument


class EventListViewSet(CreateModelMixin, DocumentViewSet):
    document = EventDocument
    serializer_class = {
        "list": EventDocumentSerializer,
        "create": EventCreateUpdateSerializer,
    }
    permission_classes = {
        "list": [StatusPermissions],
        "create": [MailIsConfirmed],
    }

    filter_backends = [
        CompoundSearchFilterBackend,
        FilteringFilterBackend,
    ]

    filter_fields = {
        "country": "country.id",
        "city": "city.id",
        "category": "categories.id",
        "date": "date",
    }

    search_fields = {
        "title": {"fuzziness": "AUTO"},
        "short_description": {"fuzziness": "AUTO"},
    }

    def get_queryset(self):
        qs: Search = super().get_queryset()
        user = self.request.user
        status = self.request.query_params.get("status")

        if status not in set(EventStatus):
            raise ValidationError(
                "Параметр 'status' не указан или имеет неверное значение. "
                + f"Ожидаемые значения: {[e.value for e in EventStatus]}"
            )

        # "Мои встречи": пользователь является участником/организатором
        if status in [EventStatus.UPCOMING, EventStatus.PAST, EventStatus.DRAFT]:
            qs = qs.filter(
                Q("term", **{"participants.user.id": user.id})
                | Q("term", **{"organizer.id": user.id})
            )

        # все события опубликованы, если статус не DRAFT
        qs = qs.filter(Q("term", is_draft=status == EventStatus.DRAFT))

        # PAST включает в себя начавшиеся и прошедшие события, все др. статусы - будущие
        if status == EventStatus.PAST:
            qs = qs.filter(Q("range", start_timestamp={"lte": now().timestamp()}))
        else:
            qs = qs.filter(Q("range", start_timestamp={"gt": now().timestamp()}))

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

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        min_age = self.request.query_params.get("min_age")
        max_age = self.request.query_params.get("max_age")
        if min_age:
            queryset = queryset.filter(Q("range", **{"max_age": {"gte": min_age}}))
        if max_age:
            queryset = queryset.filter(Q("range", **{"min_age": {"lte": max_age}}))
        return queryset

    def get_permissions(self):
        self.permission_classes = self.permission_classes[self.action]
        return super(EventListViewSet, self).get_permissions()

    def get_serializer_class(self):
        return self.serializer_class[self.action]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        status = self.request.query_params.get("status")
        is_auth = self.request.user.is_authenticated

        if status != EventStatus.POPULAR and is_auth:
            context["user"] = self.request.user

        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response_data = {"events": response.data}
        status = request.query_params.get("status", None)

        if status == EventStatus.PUBLISHED:
            serializer = FilterQuerySerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            response_data["filters"] = serializer.data

        if self.request.user.is_authenticated:
            unread_notify = self.request.user.notifications.filter(read=False).count()
            response_data["unread_notify"] = unread_notify

        return Response(response_data)
