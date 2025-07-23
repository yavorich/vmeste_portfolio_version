import httpx as requests
from rest_framework.exceptions import ParseError

from apps.payment.encrypt import TinkoffTokenEncrypter
from apps.payment.tinkoff_api.base import BaseTinkoffPaymentApi
from config.settings import SAFE_TINKOFF_TERMINAL_KEY, SAFE_TINKOFF_PASSWORD


class SafeTinkoffPaymentApi(BaseTinkoffPaymentApi):
    _terminal_key = SAFE_TINKOFF_TERMINAL_KEY
    encrypter = TinkoffTokenEncrypter(SAFE_TINKOFF_PASSWORD)

    def add_customer(self, user_uuid) -> bool:
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/AddCustomer/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key + "E2C",
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

            print(data)
            raise ParseError(data)

        return True

    def add_card(self, user_uuid):
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/AddCard/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key + "E2C",
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

        return data["PaymentURL"]

    def get_card_list(self, user_uuid):
        response = requests.post(
            url=f"{self.base_url}/e2c/v2/GetCardList/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key + "E2C",
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

            print(data)
            raise ParseError(data)

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
                    "TerminalKey": self.terminal_key + "E2C",
                    "CustomerKey": str(user_uuid),
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

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
        receipt_data=None,
        deal_id=None,
        two_stage=False,
    ):
        price = round(amount * 100)
        if receipt_data is None:
            receipt_items = [
                {
                    "Name": product_name,
                    "Price": price,
                    "Quantity": 1,
                    "Amount": price,
                    "Tax": "none",
                }
            ]
        else:
            receipt_items = [
                {
                    "Name": _data[0],
                    "Price": round(_data[1] * 100),
                    "Quantity": 1,
                    "Amount": round(_data[1] * 100),
                    "Tax": "none",
                }
                for _data in receipt_data
            ]

        data = {
            "TerminalKey": self.terminal_key,
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
                "Taxation": "usn_income",
                "Items": receipt_items,
            },
        }

        if deal_id is None:
            data.update(
                {
                    "CreateDealWIthType": "NN",
                }
            )
        else:
            data.update(
                {
                    "CreateDealWIthType": False,
                    "DealId": deal_id,
                }
            )

        response = requests.post(
            url=f"{self.base_url}/v2/Init/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(data),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

        return {
            "payment_id": data["PaymentId"],
            "payment_url": data["PaymentURL"],
        }

    def confirm_payment(self, *, payment_id, amount=None):
        data = {
            "TerminalKey": self.terminal_key,
            "PaymentId": payment_id,
        }
        if amount is not None:
            data["Amount"] = round(amount * 100)

        response = requests.post(
            url=f"{self.base_url}/v2/Confirm",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(data),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            if (
                data["ErrorCode"] == "4"
                and data["Details"] == "Изменение статуса недопустимо."
            ):
                return

            print(data)
            raise ParseError(data)

    def get_state(self, payment_id):
        response = requests.post(
            f"{self.base_url}/v2/GetState",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key,
                    "PaymentId": payment_id,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

        return data["Status"]

    def transfer_init(self, *, order_uuid, deal_id, amount, card_id, final=True):
        price = round(amount * 100)
        response = requests.post(
            f"{self.base_url}/e2c/v2/Init/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key + "E2C",
                    "Amount": price,
                    "OrderId": str(order_uuid),
                    "CardId": card_id,
                    "DealId": deal_id,
                    "FinalPayout": final,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

        return data["PaymentId"]

    def transfer_payment(self, payment_id):
        response = requests.post(
            f"{self.base_url}/e2c/v2/Payment/",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key + "E2C",
                    "PaymentId": payment_id,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        return data["Success"]

    def create_sp_deal(self):
        response = requests.post(
            f"{self.base_url}/v2/createSpDeal",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key,
                    "SpDealType": "1N",
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)

        return data["SpAccumulationId"]

    def close_sp_deal(self, sp_accumulation_id):
        response = requests.post(
            f"{self.base_url}/v2/closeSpDeal",
            headers={"Content-Type": "application/json"},
            json=self.encrypter.encrypt(
                {
                    "TerminalKey": self.terminal_key,
                    "SpAccumulationId": sp_accumulation_id,
                }
            ),
        )
        self._check_status_code(response.status_code)

        data = response.json()
        if not data["Success"]:
            print(data)
            raise ParseError(data)
