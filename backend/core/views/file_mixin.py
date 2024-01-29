import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin


class FileModelMixin(CreateModelMixin, UpdateModelMixin):
    @staticmethod
    def get_form_data(request):
        data = request.data.dict()
        try:
            text_data = json.loads(data["text"])
        except json.decoder.JSONDecodeError:
            text_data = data["text"]
        return {"file": data["file"], "text": text_data}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.get_form_data(request))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=self.get_form_data(request), partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
