from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.chat.consumers import ChatConsumer
from apps.chat.views import ChatEventViewSet, MessageListView, MessageSendView

app_name = "chat"


router = DefaultRouter()
router.register("chats", ChatEventViewSet, basename="chat")


urlpatterns = [
    path(
        "chats/<str:event_pk>/messages/", MessageListView.as_view(), name="message-list"
    ),
    path(
        "chat/<str:event_pk>/send_message/",
        MessageSendView.as_view(),
        name="message-send",
    ),
] + router.urls

websocket_urlpatterns = [
    path("chat/", ChatConsumer.as_asgi()),
]
