from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path(
        "notifications/",
        views.NotificationListUpdateApiView.as_view(),
        name="notifications-list-update",
    ),
]
