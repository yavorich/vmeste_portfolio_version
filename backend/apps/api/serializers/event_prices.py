from decimal import Decimal

from rest_framework.serializers import Serializer, DecimalField, SerializerMethodField
from apps.api.models import Theme

from config.settings import TINKOFF_SAFE_PAYMENT_COMMISSION
from core.defaults import DECIMAL_RUB


class EventPriceDetailsSerializer(Serializer):
    price = DecimalField(min_value=0, write_only=True, **DECIMAL_RUB)

    bank_fee = SerializerMethodField()
    service_fee = SerializerMethodField()
    net_income = SerializerMethodField()

    def get_bank_fee(self, obj):
        return round(obj["price"] * Decimal(TINKOFF_SAFE_PAYMENT_COMMISSION), 2)

    def get_service_fee(self, obj):
        prof_theme = Theme.objects.filter(payment_type=Theme.PaymentType.PROF).first()
        commission_percent = prof_theme.commission_percent
        return round(obj["price"] * commission_percent, 2)

    def get_net_income(self, obj):
        bank_fee = self.get_bank_fee(obj)
        service_fee = self.get_service_fee(obj)
        return round(obj["price"] - bank_fee - service_fee, 2)
