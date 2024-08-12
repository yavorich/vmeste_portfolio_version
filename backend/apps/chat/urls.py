from django.urls import path

from apps.chat.consumers import ChatConsumer
from apps.chat.views import ChatListView, MessageListView, MessageSendView

app_name = "chat"

urlpatterns = [
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path("chat/<str:event_pk>/", MessageListView.as_view(), name="message-list"),
    path(
        "chat/<str:event_pk>/send_message/",
        MessageSendView.as_view(),
        name="message-send",
    ),
]

websocket_urlpatterns = [
    path("chat/", ChatConsumer.as_asgi()),
]
