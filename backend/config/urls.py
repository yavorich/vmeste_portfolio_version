from django.contrib import admin
from django.urls import path, include

# from api.urls import urlpatterns as api_urlpatterns
# from chat.urls import urlpatterns as chat_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'api/v1/', include(
            [
                path("", include("api.urls", namespace="api")),
                path("", include("chat.urls", namespace="chat")),
            ]
        )
    ),
]
