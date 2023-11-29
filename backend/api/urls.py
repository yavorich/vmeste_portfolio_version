from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path("events/", views.EventListView.as_view(), name="events-list"),
]
