import base64
import binascii
import filetype

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from rest_framework.fields import empty, CharField, IntegerField, URLField

from rest_framework.serializers import ValidationError, Serializer
from drf_extra_fields.fields import Base64FileField, Base64FieldMixin

from .mixins import UrlWithoutDomainMixin


class Base64FileField(Base64FileField):
    INVALID_FILE_MESSAGE = "Некорректный файл"
    INVALID_TYPE_MESSAGE = "Некорректное расширение файла"

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
            if file_extension is None:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

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


class FileSerializer(Serializer):
    name = CharField()
    body = CharField(write_only=True)
    extension = CharField(read_only=True)
    size = IntegerField(read_only=True)
    url = URLField(read_only=True)


class NameBodyMixin:
    file_serializer_class = None

    def run_validation(self, data=empty):
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        self.file_serializer = self.file_serializer_class(data=data)
        self.file_serializer.is_valid(raise_exception=True)
        base64_data = self.file_serializer.validated_data["body"]

        value = self.to_internal_value(base64_data)
        self.run_validators(value)
        return value

    def get_file_name(self, decoded_file):
        filename_with_extension = self.file_serializer.validated_data["name"]
        dot_i = filename_with_extension.find(".")
        if dot_i != -1:
            return filename_with_extension[:dot_i]

    def get_file_extension(self, filename, decoded_file):
        filename_with_extension = self.file_serializer.validated_data["name"]
        return self._get_file_extension(filename_with_extension)

    @staticmethod
    def _get_file_extension(filename):
        file_name_with_extension_split = filename.split("/")[-1].split(".")
        if len(file_name_with_extension_split) > 1:
            return file_name_with_extension_split[-1]

    @staticmethod
    def _get_file_name_extension(filename):
        file_name_with_extension_split = filename.split("/")[-1].split(".")
        if len(file_name_with_extension_split) > 1:
            return (
                "".join(file_name_with_extension_split[:-1]),
                file_name_with_extension_split[-1],
            )
        else:
            return file_name_with_extension_split[0], None


class NameFileField(NameBodyMixin, Base64FileField):
    file_serializer_class = FileSerializer


class NameSizeFileField(NameFileField):
    def to_representation(self, value) -> FileSerializer:
        if not value:
            return None

        try:
            size = value.size
        except FileNotFoundError:
            size = 0

        filename, extension = self._get_file_name_extension(value.name)
        return FileSerializer(
            {
                "name": filename,
                "extension": extension,
                "size": size,
                "url": super(NameSizeFileField, self).to_representation(value),
            }
        ).data


class UrlFileField(UrlWithoutDomainMixin, Base64FileField):
    pass


class NameUrlFileField(UrlWithoutDomainMixin, NameFileField):
    pass


class NameSizeUrlFileField(NameSizeFileField, UrlWithoutDomainMixin, NameFileField):
    pass
