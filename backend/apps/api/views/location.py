from django.core.cache import cache
from django.core.management import call_command
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    GeoSpatialOrderingFilterBackend,
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
)
from elasticsearch.exceptions import NotFoundError
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter

from apps.api.documents import LocationDocument
from apps.api.serializers import (
    LocationDocumentSerializer,
    LocationCreateSerializer,
    CountrySerializer,
    CitySerializer,
)
from apps.api.models import Country, City, Location
from core.cache.functools import get_or_cache
from .mixins import LocationMixin


class LocationListViewSet(CreateModelMixin, DocumentViewSet):
    document = LocationDocument
    serializer_class = {
        "list": LocationDocumentSerializer,
        "create": LocationCreateSerializer,
    }
    permission_classes = [AllowAny]

    filter_backends = [
        CompoundSearchFilterBackend,
        GeoSpatialOrderingFilterBackend,
        FilteringFilterBackend,
    ]

    filter_fields = {
        "city": "city.id",
    }

    search_fields = ("name", "address")

    geo_spatial_ordering_fields = {
        "coords": "coords",
    }

    def get_queryset(self):
        try:
            qs = super().get_queryset().filter("term", status=Location.Status.VERIFIED)
            query_params = self.request.query_params
            if not query_params.get("search") and not query_params.get("ordering"):
                qs = qs.sort("-id")
            total = qs.count()
            return qs[:total]
        except NotFoundError:
            call_command("search_index", "--rebuild", "-f")
            return self.get_queryset()

    def get_serializer_class(self):
        return self.serializer_class[self.action]


class CountryListView(LocationMixin, ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CountrySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    queryset = Country.objects.order_by("name")


class CityListView(LocationMixin, ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    queryset = City.objects.order_by("name")

    def get(self, request, *args, **kwargs):
        if self.check_filter():
            return super().get(request, *args, **kwargs)

        return get_or_cache(f"country_cities_{self.kwargs['pk']}", 60 * 60 * 24)(
            super().get
        )(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(country_id=self.kwargs["pk"])
