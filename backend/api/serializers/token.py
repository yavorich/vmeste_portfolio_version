from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.fields["password"].required = False

    def validate(self, attrs):
        attrs.update({"password": ""})
        return super(UserTokenObtainPairSerializer, self).validate(attrs)


class UserTokenRefreshSerializer(TokenRefreshSerializer):
    pass
