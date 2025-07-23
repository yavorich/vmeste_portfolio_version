from django.db.models import Manager
from .tinkoff_transaction import TinkoffTransaction, ProductType


class OrgPaymentManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product_type=ProductType.ORGANIZATION)


class PartPaymentManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(product_type=ProductType.PARTICIPANCE)


class OrgPaymentProxy(TinkoffTransaction):
    objects = OrgPaymentManager()

    class Meta:
        proxy = True
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты организаторов"


class PartPaymentProxy(TinkoffTransaction):
    objects = PartPaymentManager()

    class Meta:
        proxy = True
        verbose_name = "Оплата"
        verbose_name_plural = "Оплаты присоединившихся"
