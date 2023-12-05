import random
from api.tasks import send_mail_confirmation_code


def generate_confirmation_code():
    return "".join([str(random.randint(0, 9)) for _ in range(5)])


def send_confirmation_code(user, confirm_type):
    if confirm_type == "mail":
        send_mail_confirmation_code.delay(user.email, user.confirmation_code)
    elif confirm_type == "phone":
        pass  # нужен смс-сервис
