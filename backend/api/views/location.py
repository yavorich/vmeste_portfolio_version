from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    GeoSpatialOrderingFilterBackend,
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
)
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter
from rest_framework.exceptions import ParseError, ValidationError
import json

from api.documents import LocationDocument
from api.permissions import MailIsConfirmed
from api.serializers import (
    LocationDocumentSerializer,
    LocationCreateSerializer,
    CountrySerializer,
    CitySerializer,
)
from api.models import Country, City, Event, Location


class LocationListViewSet(CreateModelMixin, DocumentViewSet):
    document = LocationDocument
    serializer_class = {
        "list": LocationDocumentSerializer,
        "create": LocationCreateSerializer,
    }
    permission_classes = [MailIsConfirmed]

    filter_backends = [
        GeoSpatialOrderingFilterBackend,
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
    ]

    filter_fields = {
        "city_id": "city.id",
    }

    search_fields = {
        "name": {"fuzziness": "AUTO"},
        "address": {"fuzziness": "AUTO"},
    }

    geo_spatial_ordering_fields = {
        "coords": "coords",
    }

    def get_queryset(self):
        qs = super().get_queryset().filter("term", status=Location.Status.VERIFIED)
        query_params = self.request.query_params
        if not query_params.get("search") and not query_params.get("ordering"):
            qs = qs.sort("-id")
        return qs

    def get_serializer_class(self):
        return self.serializer_class[self.action]


class CountryListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CountrySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    queryset = Country.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        _filter = self.request.query_params.get("filter")
        if _filter is None:
            raise ParseError("Параметр filter должен быть указан")
        _filter = json.loads(_filter)
        if not isinstance(_filter, bool):
            raise ValidationError("Параметр filter должен иметь значение true/false")

        if _filter:
            gender = getattr(self.request.user, "gender", None)
            actual_events = (
                Event.objects.filter(is_close_event=False)
                .filter_upcoming()
                .filter_has_free_places(gender)
            )
            queryset = queryset.filter(events__in=actual_events).distinct()
        return queryset


class CityListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        queryset = City.objects.filter(country=self.kwargs["pk"])
        _filter = self.request.query_params.get("filter")
        if _filter is None:
            raise ParseError("Параметр filter должен быть указан")
        _filter = json.loads(_filter)
        if not isinstance(_filter, bool):
            raise ValidationError("Параметр filter должен иметь значение true/false")

        if isinstance(_filter, bool) and _filter:
            print(self.request.query_params.get("filter", False))
            gender = getattr(self.request.user, "gender", None)
            actual_events = (
                Event.objects.filter(is_close_event=False)
                .filter_upcoming()
                .filter_has_free_places(gender)
            )
            queryset = queryset.filter(events__in=actual_events).distinct()
        return queryset
