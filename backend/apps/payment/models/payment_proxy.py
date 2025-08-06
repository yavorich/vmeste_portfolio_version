from django.db.models import Manager
from .tinkoff_transaction import TinkoffTransaction, ProductType, TransactionType


class OrgPaymentManager(Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                product_type=ProductType.ORGANIZATION,
                transaction_type=TransactionType.PAYMENT,
                status=TinkoffTransaction.Status.SUCCESS,
            )
        )


class PartPaymentManager(Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                product_type=ProductType.PARTICIPANCE,
                transaction_type=TransactionType.PAYMENT,
                status=TinkoffTransaction.Status.SUCCESS,
            )
        )


class OrgPaymentProxy(TinkoffTransaction):
    objects = OrgPaymentManager()

    class Meta:
        proxy = True
        app_label = "payment"
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты организаторов"


class PartPaymentProxy(TinkoffTransaction):
    objects = PartPaymentManager()

    class Meta:
        proxy = True
        app_label = "payment"
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты присоединившихся"
