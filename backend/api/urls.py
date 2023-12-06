from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("events/", views.EventListView.as_view(), name="events-list"),
    path("event/<int:pk>/", views.EventDetailView.as_view(), name="event-detail"),
    path(
        "events/published/<int:id>/<str:action>/",
        views.EventSignView.as_view(),
        name="event-sign",
    ),
    path("auth/send_code", views.AuthSendCodeView.as_view(), name="auth-code"),
    path("auth/", views.AuthView.as_view(), name="auth"),
    path(
        "profile/",
        views.ProfileUpdateViewSet.as_view(
            {"put": "update", "patch": "partial_update"}
        ),
        name="my-profile",
    ),
    path(
        "profile/<int:pk>/",
        views.ProfileDetailViewSet.as_view({"get": "retrieve", "delete": "destroy"}),
        name="user-profile",
    ),
]
