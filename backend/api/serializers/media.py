from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import (
    ModelSerializer,
    FileField,
)

from api.models import EventMedia
from core.utils import validate_file_size


class FileBulkListSerializer(BulkListSerializer):
    file = FileField(validators=[validate_file_size], read_only=False)


class EventMediaBulkCreateSerializer(BulkSerializerMixin, ModelSerializer):

    class Meta:
        list_serializer_class = FileBulkListSerializer
        model = EventMedia
        fields = ["id", "file"]

    def create(self, validated_data):
        validated_data["event"] = self.context["event"]
        validated_data["author"] = self.context["user"]

        return super().create(validated_data)


class EventMediaListSerializer(ModelSerializer):

    class Meta:
        model = EventMedia
        fields = [
            "id",
            "file",
            "uploaded_at",
        ]
