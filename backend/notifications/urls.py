from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path(
        "notifications/",
        views.NotificationListUpdateApiView.as_view(),
        name="notifications-list-update",
    ),
    path('push_token/', views.PushTokenView.as_view(), name='push_token'),
]
