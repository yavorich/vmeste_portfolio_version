from rest_framework.serializers import ModelSerializer

from apps.api.models import Occupation


class OccupationSerializer(ModelSerializer):
    class Meta:
        model = Occupation
        fields = ["id", "title"]
