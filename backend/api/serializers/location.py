from rest_framework.serializers import (
    ModelSerializer,
    CharField,
    FloatField,
    IntegerField,
    ValidationError,
    FileField,
    SerializerMethodField,
)
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from api.models import Location, Country, City
from api.documents import LocationDocument
from core.utils import validate_file_size


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ["id", "name"]


class CitySerializer(ModelSerializer):
    country_id = IntegerField(source="country.id")

    class Meta:
        model = City
        fields = ["id", "name", "country_id"]


class LocationSerializer(ModelSerializer):
    country = CharField(source="country.name")
    city = CharField(source="city.name")

    class Meta:
        model = Location
        fields = ["name", "latitude", "longitude", "address", "country", "city"]

    def __init__(self, *args, **kwargs):
        remove_fields = kwargs.pop("remove_fields", None)
        super(LocationSerializer, self).__init__(*args, **kwargs)

        if remove_fields:
            for field_name in remove_fields:
                self.fields.pop(field_name)


class LocationDocumentSerializer(DocumentSerializer):
    latitude = FloatField(source="coords.lat")
    longitude = FloatField(source="coords.lon")
    cover = SerializerMethodField()

    class Meta:
        document = LocationDocument
        fields = [
            "id",
            "cover",
            "name",
            "latitude",
            "longitude",
            "address",
            "discount",
        ]

    def get_cover(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.cover) if obj.cover else None


class LocationCreateSerializer(ModelSerializer):
    cover = FileField(validators=[validate_file_size])

    class Meta:
        model = Location
        fields = [
            "id",
            "cover",
            "name",
            "latitude",
            "longitude",
            "address",
            "country",
            "city",
        ]

    def create(self, validated_data):
        if Location.objects.filter(
            **{
                k: validated_data[k]
                for k in validated_data
                if k not in ["latitude", "longitude"]
            }
        ).exists():
            raise ValidationError({"error": "Такая локация уже существует"})

        validated_data["status"] = Location.Status.RECOMMENDED
        return super().create(validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {"id": data["id"]}
