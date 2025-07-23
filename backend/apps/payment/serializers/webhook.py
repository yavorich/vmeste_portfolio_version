from decimal import Decimal

from rest_framework.serializers import (
    Serializer,
    CharField,
    ValidationError,
    IntegerField,
    BooleanField,
)

from config.settings import TINKOFF_TERMINAL_KEY, SAFE_TINKOFF_TERMINAL_KEY


class PaymentWebhookSerializer(Serializer):
    TerminalKey = CharField(source="terminal_key")
    Amount = IntegerField(source="amount")
    OrderId = CharField(source="order_uuid")
    Success = BooleanField(source="success")
    Status = CharField(source="status")
    PaymentId = CharField(source="payment_id")
    ErrorCode = IntegerField(source="error_code")
    Message = CharField(source="message", required=False)
    Details = CharField(source="details", required=False)
    RebillId = CharField(source="rebill_id", required=False)
    CardId = CharField(source="card_id")
    Pan = CharField(source="pan")
    ExpDate = IntegerField(source="exp_code")
    Token = CharField(source="token")

    @staticmethod
    def validate_TerminalKey(value):
        if value not in [TINKOFF_TERMINAL_KEY, SAFE_TINKOFF_TERMINAL_KEY]:
            raise ValidationError

        return value

    @staticmethod
    def validate_Amount(value):
        return Decimal(value / 100)

    @staticmethod
    def validate_Token(value):
        # TODO validate token
        return value
