from hashlib import sha256

class TinkoffTokenEncrypter:
    _password = None

    def __init__(self, password):
        self._password = password

    @property
    def password(self):
        return self._password

    def encrypt(self, data: dict):
        data["Token"] = self.get_token(data)
        return data

    def get_token(self, data):
        key_value = [
            (key, self._check_value(value))
            for key, value in data.items()
            if not isinstance(value, (dict, list))
        ]
        key_value.append(("Password", self.password))
        key_value.sort()  # by key
        values = "".join(map(lambda x: str(x[1]), key_value)).encode("utf-8")
        return sha256(values).hexdigest()

    @staticmethod
    def _check_value(value):
        if isinstance(value, bool):
            if value:
                return "true"
            else:
                return "false"

        return value
