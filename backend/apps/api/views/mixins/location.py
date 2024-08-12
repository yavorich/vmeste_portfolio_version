import json
from rest_framework.exceptions import ParseError

from apps.api.models import Event


class LocationMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        _filter = self.request.query_params.get("filter")
        if _filter is None:
            raise ParseError("Параметр filter должен быть указан")
        _filter = json.loads(_filter)
        if not isinstance(_filter, bool):
            raise ParseError("Параметр filter должен иметь значение true/false")

        if isinstance(_filter, bool) and _filter:
            gender = getattr(self.request.user, "gender", None)
            actual_events = (
                Event.objects.filter(is_close_event=False)
                .filter_upcoming()
                .filter_has_free_places(gender)
            )
            queryset = queryset.filter(events__in=actual_events).distinct()
        return queryset
