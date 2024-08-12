from rest_framework.permissions import BasePermission

from apps.api.enums import EventStatus


class StatusPermissions(BasePermission):
    message = "Пользователь не аутентифицирован."

    def has_permission(self, request, view):
        status = request.query_params.get("status", None)

        if status in [EventStatus.UPCOMING, EventStatus.PAST, EventStatus.DRAFT]:
            return request.user.is_authenticated

        return True
