from rest_framework import serializers

from api.models import Docs


class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = ["text"]
