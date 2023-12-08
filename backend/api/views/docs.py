from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from api.models import Docs
from api.serializers import DocsSerializer


class DocsView(RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DocsSerializer

    def get_object(self):
        name = self.request.query_params.get("name")
        return get_object_or_404(Docs, name=name)
