from rest_framework.mixins import ListModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from django.shortcuts import get_object_or_404, get_list_or_404

from api.models import Docs
from api.serializers import DocsSerializer


class DocsViewSet(ListModelMixin, UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DocsSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        return get_list_or_404(Docs.objects.filter(name=name))

    def get_object(self):
        name = self.request.query_params.get("name")
        return get_object_or_404(Docs, name=name)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["user"] = self.request.user
        return context

    @action(methods=["post"], detail=False)
    def apply(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response(data=response.data[0], status=HTTP_200_OK)
