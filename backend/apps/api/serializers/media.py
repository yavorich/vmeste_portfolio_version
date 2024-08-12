from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import (
    ModelSerializer,
    FileField,
    SerializerMethodField,
)

from apps.api.models import EventMedia
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
    size = SerializerMethodField()

    class Meta:
        model = EventMedia
        fields = [
            "id",
            "file",
            "size",
            "mimetype",
            "preview",
            "uploaded_at",
        ]

    def get_size(self, obj: EventMedia):
        return obj.file.size
