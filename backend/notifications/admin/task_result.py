from django.contrib import admin
from django_celery_results.admin import TaskResult, GroupResult

admin.site.unregister(TaskResult)
admin.site.unregister(GroupResult)
