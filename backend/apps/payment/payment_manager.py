from django.urls import reverse

from core.singleton import SingletonMeta
from apps.payment.models import TinkoffTransaction
from apps.payment.payment_api import TinkoffPaymentApi


class PaymentManager(metaclass=SingletonMeta):
    payment_api = TinkoffPaymentApi()

    def buy(self, event, user, product_type, amount, base_url):
        transaction = TinkoffTransaction(
            user=user,
            event=event,
            product_type=product_type,
            price=amount,
        )
        payment_data = self.payment_api.init_payment(
            amount=amount,
            order_uuid=transaction.uuid,
            product_name=transaction.product_name,
            description=transaction.description,
            user_uuid=user.uuid,
            email=user.email,
            phone_number=user.phone_number.as_e164,
            notification_url=base_url + reverse("payment_webhook"),
            success_url=base_url + reverse("payment_success"),
            fail_url=base_url + reverse("payment_fail"),
        )
        for attr, value in payment_data.items():
            setattr(transaction, attr, value)

        transaction.save()

        return {"payment_url": payment_data["payment_url"], "payment_uuid": transaction.uuid}
