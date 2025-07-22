from rest_framework.serializers import ModelSerializer

from apps.api.models import LegalEntity


class LegalEntitySerializer(ModelSerializer):
    class Meta:
        model = LegalEntity
        fields = (
            "company_name",
            "legal_address",
            "full_name",
            "phone_number",
            "director_full_name",
            "director_phone_number",
            "inn",
            "ogrn",
            "bic",
            "bank_name",
            "current_account",
            "sites",
            "confirmed",
        )
        read_only_fields = ("confirmed",)
