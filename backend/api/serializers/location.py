from rest_framework.serializers import ModelSerializer, CharField
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from api.models import Location
from api.documents import LocationDocument


class LocationSerializer(ModelSerializer):
    country = CharField(source="country.name")
    city = CharField(source="city.name")

    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude", "address", "country", "city"]

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop('remove_fields', None)
        super(LocationSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)


class LocationDocumentSerializer(DocumentSerializer):

    class Meta:
        document = LocationDocument


class LocationCreateSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = []
