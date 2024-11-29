import os
from urllib.parse import unquote

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField

from drf_extra_fields.fields import Base64ImageField, Base64FieldMixin

from .file_field import NameBodyMixin
from .mixins import UrlWithoutDomainMixin


class MediaLinkImageField(Base64ImageField):
    def to_internal_value(self, data):
        if data in self.EMPTY_VALUES:
            return None

        if isinstance(data, str) and data.startswith(settings.MEDIA_URL):
            # Try to decode the file. Return validation error if it fails.

            url_path = unquote(data)
            path = os.path.join(
                settings.MEDIA_ROOT, url_path.replace(settings.MEDIA_URL, "")
            )
            try:
                media_file = default_storage.open(path)
            except FileNotFoundError:
                raise ValidationError("Not found")

            decoded_file = media_file.read()

            # Generate file name:
            file_name_with_extension = data.split("/")[-1]
            dot_i = file_name_with_extension.find(".")

            file_name = file_name_with_extension[:dot_i]
            # Get the file name extension:
            file_extension = file_name_with_extension[dot_i + 1 :]
            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            complete_file_name = file_name + "." + file_extension
            data = ContentFile(decoded_file, name=complete_file_name)
            return super(Base64FieldMixin, self).to_internal_value(data)
        raise ValidationError("Must be link to media")


class FileShortSerializer(Serializer):
    name = CharField()
    body = CharField()


class NameImageField(NameBodyMixin, Base64ImageField):
    """
    ImageField с явным указанием расширения
    """

    file_serializer_class = FileShortSerializer


class NameUrlImageField(UrlWithoutDomainMixin, NameImageField):
    pass


class MediaLinkUrlImageField(UrlWithoutDomainMixin, MediaLinkImageField):
    pass
