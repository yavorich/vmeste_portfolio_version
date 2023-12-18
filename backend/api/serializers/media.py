import base64
import filetype
import binascii

from rest_framework_bulk.serializers import BulkListSerializer, BulkSerializerMixin
from rest_framework.serializers import ModelSerializer, SerializerMethodField, CharField
from rest_framework.serializers import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import Base64FileField, Base64FieldMixin
from rest_framework.settings import api_settings

from api.models import EventMedia


def validate_file_size(file):
    """Установить ограничение для загружаемых файлов"""
    if not file:
        return
    max_size = 50 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError("Размер файла не должен превышать 50 МБ.")


class UrlWithoutDomainMixin:
    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, "use_url", api_settings.UPLOADED_FILES_USE_URL)
        if use_url:
            try:
                url = value.url
            except AttributeError:
                return None

            return url

        return value.name


class CustomFileField(UrlWithoutDomainMixin, Base64FileField):
    INVALID_FILE_MESSAGE = "Некорректный файл"

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            return super(Base64FieldMixin, self).to_internal_value(None)

        if isinstance(base64_data, str):
            # Strip base64 header.
            if ";base64," in base64_data:
                header, base64_data = base64_data.split(";base64,")

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)
            # Generate file name:
            file_name = self.get_file_name(decoded_file)
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = file_name + "." + file_extension
            data = ContentFile(decoded_file, name=complete_file_name)
            return super(Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError(
            _(
                "Invalid type. This is not an base64 string: {}".format(
                    type(base64_data)
                )
            )
        )

    def get_file_extension(self, filename, decoded_file):
        try:
            kind = filetype.guess(decoded_file)
            return kind.extension
        except AttributeError:
            raise ValidationError(self.INVALID_FILE_MESSAGE)


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
        extension = obj.file.path.split(".")[-1]
        with open(obj.file.path, "rb") as img_file:
            data = img_file.read()
            return "data:image/%s;base64,%s" % (extension, base64.b64encode(data))
