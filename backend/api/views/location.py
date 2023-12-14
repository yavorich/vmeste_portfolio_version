from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
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
