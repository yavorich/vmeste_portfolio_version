from rest_framework.serializers import ModelSerializer
from django.db import IntegrityError

from apps.api.models import Verification
from core.file_serializers.fields.file_field import NameSizeFileField


class VerificationSerializer(ModelSerializer):
    document_file = NameSizeFileField()

    class Meta:
        model = Verification
        fields = ("document_file", "confirmed")
        read_only_fields = ("confirmed",)
    
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            return self.context["request"].user.verification
