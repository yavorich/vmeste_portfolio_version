from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.shortcuts import get_object_or_404, get_list_or_404
from django.utils.timezone import localtime

from api.models import Docs
from api.serializers import DocsSerializer


class DocsViewSet(ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = DocsSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        return get_list_or_404(Docs.objects.filter(name=name))

    def get_object(self):
        name = self.request.query_params.get("name")
        return get_object_or_404(Docs, name=name)

    @action(methods=["post"], detail=False)
    def apply(self, request, pk=None):
        user = request.user
        obj = self.get_object()
        if obj.name == Docs.Name.AGREEMENT:  # с rules пока ничего не делаем
            if not user.agreement_applied_at:
                user.agreement_applied_at = localtime()
                user.save()
        return Response(f"{obj.name} applied.", status=HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(data=response.data[0], status=HTTP_200_OK)
