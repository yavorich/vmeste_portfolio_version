from rest_framework.exceptions import ParseError
from django.utils.translation import gettext_lazy as _


class NoCoinsError(ParseError):
    default_code = "no_coins"
    default_detail = {"detail": _("Недостаточно монет"), "code": default_code}
