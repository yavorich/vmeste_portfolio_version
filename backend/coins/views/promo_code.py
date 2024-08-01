from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from coins.serializers import PromoCodeSerializer


class ActivatePromoCodeView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PromoCodeSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        promo_code = serializer.validated_data["promo_code"]
        promo_code.activate(request.user)
        return Response({"status": "Промокод успешно активирован"})
