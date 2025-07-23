from rest_framework.serializers import ModelSerializer, FileField
from django.db import IntegrityError

from apps.api.models import LegalEntity
from core.utils import validate_file_size


class LegalEntitySerializer(ModelSerializer):
    image = FileField(validators=[validate_file_size], required=False, allow_null=True)

    class Meta:
        model = LegalEntity
        fields = (
            "image",
            "company_name",
            "legal_address",
            "resp_full_name",
            "resp_phone_number",
            "director_full_name",
            "inn",
            "bic",
            "bank_name",
            "current_account",
            "sites",
            "confirmed",
        )
        read_only_fields = ("confirmed",)

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            return self.context["request"].user.legal_entity
