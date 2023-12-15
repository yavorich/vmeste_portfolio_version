from django.urls import path
from channels.routing import URLRouter

from chat.urls import websocket_urlpatterns as chat_websocket_urlpatterns

websocket_urlpatterns = [
    path("ws/", URLRouter(chat_websocket_urlpatterns))
]
