import httpx as requests

from rest_framework.exceptions import ParseError

from apps.payment.encrypt import TinkoffTokenEncrypter
from config.settings import TINKOFF_BASE_URL, TINKOFF_TERMINAL_KEY
from core.singleton import SingletonMeta


class TinkoffPaymentApi(metaclass=SingletonMeta):
    _base_url = TINKOFF_BASE_URL
    _terminal_key = TINKOFF_TERMINAL_KEY

    encrypter = TinkoffTokenEncrypter()

    error_messages = {}

    @property
    def base_url(self):
        return self._base_url

    @property
    def terminal_key(self):
        return self._terminal_key

    def add_customer(self, user_uuid) -> bool:
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/AddCustomer/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            if (
                int(data["ErrorCode"]) == 7
                and data["Details"] == "Покупатель с таким ключом уже существует."
            ):
                return False

            raise ParseError

        return True

    def add_card(self, user_uuid):
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/AddCard/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            raise ParseError

        return data["PaymentURL"]

    def get_card_list(self, user_uuid):
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/GetCardList/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not isinstance(data, list) and not data.get("Success", True):
            if (
                int(data["ErrorCode"]) == 7
                and data["Details"] == "Покупатель не найден."
            ):
                return []

            raise ParseError

        return [
            {
                "id": card_info["CardId"],
                "pan": card_info["Pan"],
                "exp_code": card_info["ExpDate"],
            }
            for card_info in data
        ]

    def remove_customer(self, user_uuid):
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/RemoveCustomer/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            raise ParseError

    def init_payment(
        self,
        *,
        amount,
        order_uuid,
        description,
        user_uuid,
        notification_url,
        success_url,
        fail_url,
        email,
        phone_number,
        product_name,
        two_stage=False,
    ):
        price = round(amount * 100)
        response = requests.post(
            url=f"{self.base_url}/v2/Init/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "Amount": price,
                    "OrderId": str(order_uuid),
                    "Description": description,
                    "CustomerKey": str(user_uuid),
                    "PayType": "T" if two_stage else "O",
                    "NotificationURL": notification_url,
                    "SuccessURL": success_url,
                    "FailURL": fail_url,
                    "DATA": {"Phone": phone_number, "Email": email},
                    "Receipt": {
                        "Email": email,
                        "Phone": phone_number,
                        "Taxation": "osn",
                        "Items": [
                            {
                                "Name": product_name,
                                "Price": price,
                                "Quantity": 1,
                                "Amount": price,
                                "Tax": "vat10",
                            }
                        ],
                    },
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            raise ParseError

        return {
            "payment_id": data["PaymentId"],
            "payment_url": data["PaymentURL"],
        }

    def confirm_payment(self, *, payment_id, amount=None):
        data = {
            "TerminalKey": self._terminal_key,
            "PaymentId": payment_id,
        }
        if amount is not None:
            data["Amount"] = round(amount * 100)

        response = requests.post(
            url=f"{self.base_url}/v2/Confirm/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(data),
        )
        data = response.json()
        if not data["Success"]:
            raise ParseError

    def transfer_init(
        self,
        *,
        order_uuid,
        amount,
        card_id,
    ):
        price = round(amount * 100)
        response = requests.post(
            f"{self.base_url}/e2c/v2/Init/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "Amount": price,
                    "OrderId": str(order_uuid),
                    "CardId": card_id,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            raise ParseError

        return data["PaymentId"]

    def transfer_payment(self, payment_id):
        response = requests.post(
            f"{self.base_url}/e2c/v2/Payment/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self._terminal_key,
                    "PaymentId": payment_id,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            raise ParseError

    @staticmethod
    def _check_status_code(status_code):
        if status_code != 200:
            raise ParseError
