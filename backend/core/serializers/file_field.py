from rest_framework.serializers import FileField
from rest_framework.settings import api_settings


class CustomFileField(FileField):

    def to_internal_value(self, data):
        try:
            # `UploadedFile` objects should have name and size attributes.
            file_name = data.name
            file_size = data.size
        except AttributeError:
            return data

        if not file_name:
            self.fail("no_name")
        if not self.allow_empty_file and not file_size:
            self.fail("empty")
        if self.max_length and len(file_name) > self.max_length:
            self.fail("max_length", max_length=self.max_length, length=len(file_name))

        return data

    def to_representation(self, value):
        if not value:
            return None

        use_url = getattr(self, "use_url", api_settings.UPLOADED_FILES_USE_URL)
        if use_url:
            try:
                url = value.url
            except AttributeError:
                return None
            request = self.context.get("request", None)
            if request is not None:
                return request.build_absolute_uri(url)
            headers = self.context.get("headers", None)
            if headers is not None and b"host" in headers:
                host = headers[b"host"].decode()
                return f"http://{host}{url}"  # REVIEW: https не подключен?
            return url

        return value.name
