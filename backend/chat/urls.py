from django.urls import path

from chat.consumers import ChatConsumer
from chat.views import ChatListView, MessageListView, MessageSendView

app_name = "chat"

urlpatterns = [
    path("chats/", ChatListView.as_view(), name="chat-list"),
    path(
        "chat/<int:event_id>/", MessageListView.as_view(), name="message-list"
    ),
    path(
        "chat/<int:event_id>/send_message/",
        MessageSendView.as_view(),
        name="message-send",
    ),
]

websocket_urlpatterns = [
    path("chat/<int:event_id>/", ChatConsumer.as_asgi()),
]
