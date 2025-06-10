from rest_framework.serializers import ModelSerializer

from apps.api.models import Verification
from core.file_serializers.fields.file_field import NameSizeFileField


class VerificationSerializer(ModelSerializer):
    file = NameSizeFileField()

    class Meta:
        model = Verification
        fields = ("file", "confirmed")
        read_only_fields = ("confirmed",)
