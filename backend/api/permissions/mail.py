from rest_framework.permissions import BasePermission


class MailIsConfirmed(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.email_is_confirmed
        return False
