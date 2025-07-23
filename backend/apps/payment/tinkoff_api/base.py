import httpx as requests
from rest_framework.exceptions import ParseError

from config.settings import TINKOFF_BASE_URL
from core.singleton import SingletonMeta


class BaseTinkoffPaymentApi(metaclass=SingletonMeta):
    _base_url = TINKOFF_BASE_URL
    _terminal_key = None

    encrypter = None

    error_messages = {}

    @property
    def base_url(self):
        return self._base_url

    @property
    def terminal_key(self):
        return self._terminal_key

    def payment_cancel(self, payment_id):
        response = requests.post(
            f"{self.base_url}/v2/Cancel",
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

    @staticmethod
    def _check_status_code(status_code):
        if status_code != 200:
            print(status_code)
            raise ParseError
