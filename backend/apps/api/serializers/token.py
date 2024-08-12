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
    # def validate(self, attrs):
    #     refresh = self.token_class(attrs["refresh"])
    #     return {"access": str(refresh.access_token), "refresh": str(refresh)}
