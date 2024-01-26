from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.http.request import HttpRequest


class PhoneAuthBackend(ModelBackend):
    def authenticate(self, request: HttpRequest, phone_number):
        User = get_user_model()
        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
            return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
