from django.contrib import admin

from api.models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
