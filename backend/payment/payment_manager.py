from django.urls import reverse

from core.singleton import SingletonMeta
from payment.models import TinkoffTransaction
from payment.payment_api import TinkoffPaymentApi


class PaymentManager(metaclass=SingletonMeta):
    payment_api = TinkoffPaymentApi()

    def buy(self, product_type, product_id, product, user, base_url):
        transaction = TinkoffTransaction(
            product_type=product_type,
            product_id=product_id,
            price=product.price,
            user=user,
        )
        payment_data = self.payment_api.init_payment(
            amount=product.price,
            order_uuid=transaction.uuid,
            product_name=product.name,
            description=product.description,
            user_uuid=user.uuid,
            email=user.email,
            phone_number=user.phone_number,
            notification_url=base_url + reverse("payment_webhook"),
            success_url=base_url + reverse("payment_success"),
            fail_url=base_url + reverse("payment_fail"),
        )
        for attr, value in payment_data.items():
            setattr(transaction, attr, value)

        transaction.save()
        return payment_data["payment_url"], transaction.uuid
