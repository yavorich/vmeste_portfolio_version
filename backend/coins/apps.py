from django.apps import AppConfig


class CoinsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coins"
    verbose_name = "Монеты"

    def ready(self):
        from . import signals
