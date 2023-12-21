from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework.serializers import ValidationError

from api.models import EventMedia
from core.serializers import CustomFileField
from core.utils import validate_file_size, convert_file_to_base64


class EventMediaBulkCreateSerializer(BulkSerializerMixin, ModelSerializer):
    file = CustomFileField(validators=[validate_file_size])

    class Meta:
        list_serializer_class = BulkListSerializer
        model = EventMedia
        fields = [
            "file_type",
            "weight",
            "duration",
            "file",
            "file_name",
            "uploaded_at",
        ]

    def create(self, validated_data):
        validated_data["event"] = self.context["event"]
        validated_data["author"] = self.context["user"]
        if validated_data["file_type"] == EventMedia.FileType.VIDEO:
            if not validated_data.get("duration"):
                raise ValidationError(
                    "File of type 'video' must have 'duration' parameter"
                )
        if validated_data["file_type"] == EventMedia.FileType.PHOTO:
            if "duration" in validated_data:
                validated_data.pop("duration")

        return super().create(validated_data)


class EventMediaListSerializer(ModelSerializer):
    link = CharField(source="file")
    image = SerializerMethodField()

    class Meta:
        model = EventMedia
        fields = [
            "id",
            "file_type",
            "link",
            "weight",
            "duration",
            "uploaded_at",
            "image",
        ]

    def get_image(self, obj: EventMedia):
        return convert_file_to_base64(obj.file)
