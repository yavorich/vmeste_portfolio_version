import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
celery_app = Celery("config", broker=settings.CELERY_BROKER_URL)
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()

celery_app.conf.beat_schedule = {
    "daily_event": {
        "task": "notifications.tasks.create_daily_event_notifications",
        "schedule": crontab("0", "12"),  # ежедневно в 12:00
    }
}
