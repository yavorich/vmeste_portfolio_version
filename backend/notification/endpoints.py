from django.urls import path

from . import views


urlpatterns = [
    path('push_token/', views.PushTokenView.as_view(), name='push_token'),
]
