from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    GeoSpatialOrderingFilterBackend,
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
)
from rest_framework.mixins import CreateModelMixin

from api.documents import LocationDocument
from api.permissions import MailIsConfirmed
from api.serializers import LocationDocumentSerializer, LocationCreateSerializer


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
        "coords": None,
    }

    def get_queryset(self):
        qs = super().get_queryset()
        query_params = self.request.query_params
        if not query_params.get("search") and not query_params.get("ordering"):
            qs = qs.sort("-id")
        return qs

    def get_serializer_class(self):
        return self.serializer_class[self.action]
