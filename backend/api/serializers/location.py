from rest_framework.serializers import ModelSerializer, CharField
from ..models import Location


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        fields = ["name", "address"]


class LocationDetailSerializer(ModelSerializer):
    country = CharField(source="country.name")
    city = CharField(source="city.name")

    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude", "address", "country", "city"]
