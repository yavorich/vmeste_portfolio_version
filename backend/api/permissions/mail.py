from rest_framework.permissions import BasePermission, SAFE_METHODS


class MailIsConfirmed(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.email_is_confirmed
        return False
