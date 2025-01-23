from django.apps import AppConfig


class AdminHistoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.admin_history"

    def ready(self):
        from . import signals
