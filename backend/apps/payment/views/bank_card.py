from rest_framework.exceptions import NotFound
from rest_framework.generics import GenericAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from apps.admin_history.models import ActionFlag, HistoryLog
from apps.payment.payment_manager import PaymentManager
from apps.payment.serializers import URLSerializer, BankCardSerializer


class BankCardAddView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = URLSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        payment_url = PaymentManager().add_card(user)
        HistoryLog.objects.log_actions(
            user_id=user.pk,
            queryset=[user],
            action_flag=ActionFlag.ADDITION,
            change_message="Привязал банковскую карту",
            is_admin=False,
        )
        serializer = self.get_serializer({"url": payment_url})
        return Response(serializer.data)


class BankCardView(RetrieveDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = BankCardSerializer

    def get_object(self):
        bank_card = PaymentManager().get_bank_card(self.request.user)
        if bank_card is None:
            raise NotFound

        return bank_card

    def destroy(self, request, *args, **kwargs):
        user = request.user
        PaymentManager().delete_bank_card(user)
        HistoryLog.objects.log_actions(
            user_id=user.pk,
            queryset=[user],
            action_flag=ActionFlag.DELETION,
            change_message="Удалил банковскую карту",
            is_admin=False,
        )
        return Response(status=HTTP_204_NO_CONTENT)