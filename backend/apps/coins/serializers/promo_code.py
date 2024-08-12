from rest_framework.exceptions import ValidationError
from rest_framework.serializers import Serializer, CharField

from apps.coins.models import PromoCode


class PromoCodeSerializer(Serializer):
    code = CharField()

    def validate(self, attrs):
        code = attrs["code"]
        user = self.context["request"].user
        promo_code = (
            PromoCode.objects.active_list()
            .filter(code=code)
            .exclude(users_activated__in=[user])
            .first()
        )
        if promo_code is None:
            raise ValidationError({"code": "Промокод не найден"})

        attrs["promo_code"] = promo_code
        return attrs
