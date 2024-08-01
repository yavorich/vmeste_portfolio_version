from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coins.serializers import BuyCoinsSerializer


class BuyCoinsView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BuyCoinsSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO возвращать ссылку на оплату
        return Response({"url": "https:/www.google.com"})
