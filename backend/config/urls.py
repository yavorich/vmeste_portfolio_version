from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/v1/",
        include(
            [
                path("", include("apps.api.urls", namespace="api")),
                path("", include("apps.chat.urls", namespace="chat")),
                path("", include("apps.notifications.urls", namespace="notifications")),
                path("coins/", include("apps.coins.urls")),
                path("payment/", include("apps.payment.urls")),
            ]
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
