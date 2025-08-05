from django_eventstream import send_event
from rest_framework.exceptions import ValidationError, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.admin_history.models import HistoryLog, ActionFlag
from apps.api.models import EventParticipant
from apps.payment.models import TinkoffTransaction, ProductType
from apps.payment.payment_manager import PaymentManager
from apps.payment.serializers import PaymentWebhookSerializer


class PaymentNotificationHookView(GenericAPIView):
    serializer_class = PaymentWebhookSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        transaction = self.get_transaction(
            validated_data["order_uuid"], validated_data["payment_id"]
        )
        if validated_data.get("deal_id") is not None:
            transaction.deal_id = validated_data["deal_id"]
        if validated_data["success"]:
            self.confirm_payment(transaction)
        else:
            transaction.status = TinkoffTransaction.Status.FAILED

        transaction.save()
        send_event(
            f"payment_{transaction.uuid}",
            "message",
            {"success": validated_data["success"]},
        )
        return Response("OK")

    @staticmethod
    def get_transaction(transaction_uuid, payment_id):
        transaction = (
            TinkoffTransaction.objects.filter(
                uuid=transaction_uuid,
                payment_id=payment_id,
                status=TinkoffTransaction.Status.PENDING,
            )
            .order_by("-created_at")
            .first()
        )
        if transaction is None:
            raise ValidationError
        return transaction

    def confirm_payment(self, transaction: TinkoffTransaction):
        transaction.status = TinkoffTransaction.Status.SUCCESS

        event = transaction.event

        match transaction.product_type:
            case ProductType.ORGANIZATION:
                event.paid_by_organizer = True
                event.save()
            case ProductType.PARTICIPANCE:
                user = transaction.user
                participant, created = EventParticipant.objects.get_or_create(
                    event=event, user=user, payed=transaction.price
                )
                if created:
                    HistoryLog.objects.log_actions(
                        user_id=user.pk,
                        queryset=[event],
                        action_flag=ActionFlag.ADDITION,
                        change_message="Записался на событие",
                        is_admin=False,
                    )

                transfer_unique_data = dict(
                    user=transaction.user,
                    event=transaction.event,
                    product_type=transaction.product_type,
                )
                transfer_transaction = PaymentManager()._get_transfer_transaction(
                    transaction_unique_data=transfer_unique_data,
                    price=event.organizer_transfer_amount,
                    deal_id=transaction.deal_id,
                )
                success = PaymentManager().transfer_to_event_organizer(transfer_transaction)
                if not success:
                    raise ParseError("Ошибка перевода")
