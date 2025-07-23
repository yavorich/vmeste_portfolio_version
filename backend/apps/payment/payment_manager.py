from django.urls import reverse
from rest_framework.exceptions import ParseError, NotFound

from core.singleton import SingletonMeta
from apps.payment.models import TinkoffTransaction
from apps.payment.tinkoff_api import TinkoffPaymentApi, SafeTinkoffPaymentApi


class PaymentManager(metaclass=SingletonMeta):
    payment_api = TinkoffPaymentApi()
    safe_payment_api = SafeTinkoffPaymentApi()

    def add_card(self, user):
        if self.is_added_card(user):
            raise ParseError("Карта уже добавлена")

        created = self.safe_payment_api.add_customer(user.uuid)
        payment_url = self.safe_payment_api.add_card(user.uuid)
        return payment_url

    def is_added_card(self, user):
        bank_card_info = user.bank_card
        is_saved_card = bank_card_info.bank_card_id is not None

        if is_saved_card:
            return True

        cards = self.safe_payment_api.get_card_list(user.uuid)
        if len(cards) > 0:
            card = cards[0]
            bank_card_info.save_bank_card(card)
            return True

        return False

    def get_bank_card(self, user):
        bank_card_info = user.bank_card
        is_saved_card = bank_card_info.bank_card_id is not None
        if is_saved_card:
            return bank_card_info.bank_card_data

        bank_cards = self.safe_payment_api.get_card_list(user.uuid)
        try:
            card_info = bank_cards[0]
            bank_card_info.save_bank_card(card_info)
            return card_info
        except IndexError:
            return

    def delete_bank_card(self, user):
        if not self.is_added_card(user):
            raise NotFound

        bank_card_info = user.bank_card
        self.safe_payment_api.remove_customer(user.uuid)
        bank_card_info.reset_bank_card()

    def init_event_creation_payment(self, event, user, product_type, amount, base_url):
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

        return {
            "payment_url": payment_data["payment_url"],
            "payment_uuid": transaction.uuid,
        }

    def init_event_join_payment(self, event, user, product_type, amount, base_url):
        deal_id = self.safe_payment_api.create_sp_deal()
        transaction = TinkoffTransaction(
            user=user,
            event=event,
            product_type=product_type,
            price=amount,
            deal_id=deal_id,
        )
        payment_data = self.safe_payment_api.init_payment(
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
            receipt_data=None,
            deal_id=deal_id,
        )
        for attr, value in payment_data.items():
            setattr(transaction, attr, value)

        transaction.save()

        return {
            "payment_url": payment_data["payment_url"],
            "payment_uuid": transaction.uuid,
        }

    def transfer_to_event_organizer(self, transaction: TinkoffTransaction):
        if not transaction.event:
            return

        event_organizer_user = transaction.event.organizer
        if event_organizer_user is None:
            return

        organizer_bank_card_id = event_organizer_user.bank_card.bank_card_id
        if not organizer_bank_card_id:
            return

        payment_id = self.safe_payment_api.transfer_init(
            order_uuid=transaction.uuid,
            deal_id=transaction.deal_id,
            amount=transaction.price,
            card_id=organizer_bank_card_id,
            final=True,
        )
        self.safe_payment_api.transfer_payment(payment_id=payment_id)
        self.safe_payment_api.close_sp_deal(sp_accumulation_id=transaction.deal_id)
