from rest_framework.serializers import Serializer, URLField


class URLSerializer(Serializer):
    url = URLField()
