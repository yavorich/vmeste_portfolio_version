from rest_framework.permissions import BasePermission
from .enums import EventStatus


class StatusPermissions(BasePermission):
    def has_permission(self, request, view):
        status = request.query_params.get("status", None)

        if status in [EventStatus.UPCOMING,
                      EventStatus.PAST,
                      EventStatus.DRAFT]:
            return request.user.is_authenticated

        elif status in [EventStatus.PUBLISHED,
                        EventStatus.POPULAR]:
            return True

        return False  # запрос без статуса не предусмотрен
