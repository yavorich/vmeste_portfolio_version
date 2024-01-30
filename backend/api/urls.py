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
router.register(
    r"events/(?P<event_pk>\w+)/media",
    views.EventMediaViewSet,
    basename="event-media",
)
router.register(
    "docs",
    views.DocsViewSet,
    basename="docs",
)
urlpatterns = [
    path("", include(router.urls)),
    path(
        "events/",
        views.EventListViewSet.as_view({"get": "list", "post": "create"}),
        name="event-list",
    ),
    re_path(
        r"^events/(?P<event_pk>[0-9]+|[0-9a-f-]+)/$",
        views.EventDetailViewSet.as_view(
            {"get": "retrieve", "patch": "partial_update"}
        ),
        name="event-detail",
    ),
    path("auth/send_code", views.AuthSendCodeView.as_view(), name="auth-code"),
    path("auth/", views.AuthView.as_view(), name="auth"),
    path(
        "profile/",
        views.SelfProfileViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="my-profile",
    ),
    path(
        "profile/<int:pk>/",
        views.AlienProfileView.as_view(),
        name="user-profile",
    ),
    path("token/", views.UserTokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", views.UserTokenRefreshView.as_view(), name="refresh"),
    path("marking/", views.EventMarkingDetailView.as_view(), name="marking"),
    path(
        "events/<str:event_pk>/participants/",
        views.EventParticipantView.as_view(),
        name="participants-list-update",
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
    path("categories/", views.ThemeListView.as_view(), name="categories_list"),
    path(
        "categories/<int:pk>/sub/",
        views.CategoryListView.as_view(),
        name="subcategories_list",
    ),
    path("interests/", views.ThemeListView.as_view(), name="interests_list"),
    path(
        "interests/<int:pk>/sub/",
        views.CategoryListView.as_view(),
        name="subinterests_list",
    ),
    path("occupations/", views.OccupationListView.as_view(), name="occupation_list"),
    path(
        "filters/fast/",
        views.EventFastFiltersListView.as_view(),
        name="fast-filter-list",
    ),
]
