from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import status

from api.serializers import UserTokenObtainPairSerializer, UserTokenRefreshSerializer


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer


class UserTokenRefreshView(TokenRefreshView):
    serializer_class = UserTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            raise PermissionDenied(detail="Refresh token invalid or expired", code=403)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)
