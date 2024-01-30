from rest_framework.permissions import BasePermission


class MailIsConfirmed(BasePermission):
    message = "Пользователь не подтвердил почту."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.email_is_confirmed
        return False


class IsMyProfile(BasePermission):
    message = "Пользователь не является владельцем профиля."

    def has_permission(self, request, view):
        return request.user.pk == view.kwargs["pk"]
