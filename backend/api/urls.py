from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register(
    "events/published",
    views.EventPublishedSignViewSet,
    basename="event-published",
)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "events/",
        views.EventListViewSet.as_view({"get": "list", "post": "create"}),
        name="event-list",
    ),
    re_path(
        r"^events/(?P<pk>[0-9]+|[0-9a-f-]+)/$",
        views.EventDetailViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update"}
        ),
        name="event-detail",
    ),
    # path(
    #     "events/published/<int:id>/<str:action>/",
    #     views.EventPublishedSignViewSet.as_view(),
    #     name="event-sign",
    # ),
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
    path("token/", views.UserTokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", views.UserTokenRefreshView.as_view(), name="refresh"),
    path("docs/", views.DocsView.as_view(), name="docs"),
    path("marking/", views.EventMarkingDetailView.as_view(), name="marking"),
    path(
        "events/<str:event_id>/participants/",
        views.EventParticipantRetrieveUpdateView.as_view(),
        name="participants-list-update",
    ),
    path(
        "events/<str:event_id>/participants/<int:id>/",
        views.EventParticipantDeleteView.as_view(),
        name="participant-delete",
    ),
    path(
        "notifications/",
        views.NotificationListUpdateApiView.as_view(),
        name="notifications-list-update",
    ),
    path(
        "support/themes/",
        views.SupportThemeListView.as_view(),
        name="support-theme-list",
    ),
    path(
        "support/",
        views.SupportMessageCreateView.as_view(),
        name="support-message-create",
    ),
    path(
        "places/",
        views.LocationListViewSet.as_view({"get": "list", "post": "create"}),
        name="places-list-create",
    ),
    path("countries/", views.CountryListView.as_view(), name="country-list"),
    path(
        "countries/<int:pk>/cities/",
        views.CityListView.as_view(),
        name="city-list",
    ),
    path("interests/", views.InterestListView.as_view(), name="interest_list"),
    path("occupations/", views.OccupationListView.as_view(), name="occupation_list"),
    path(
        "event/<str:pk>/media/",
        views.EventMediaListCreateView.as_view(),
        name="event-media",
    ),
]
