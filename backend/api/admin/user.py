from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from api.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "avatar",
        "first_name",
        "last_name",
        "phone_number",
        "email",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        "get_interests",
        "occupation",
        # "position", - должность
        "about_me",
        "agreement_applied_at",
        "is_active",
    ]
    # list_editable =
    filter_horizontal = ("interests", )

    readonly_fields = []
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["block_users", "unblock_users"]

    @admin.display(description="Категории")
    def get_interests(self, obj):
        return self.links_to_objects(obj.interests.all())

    @classmethod
    def links_to_objects(cls, objects):
        rel_list = "<ol>"
        for obj in objects:
            link = reverse("admin:api_category_change", args=[obj.id])
            rel_list += "<li><a href='%s'>%s</a></li>" % (link, obj.title)
        rel_list += "</ol>"
        return format_html(rel_list)

    @admin.action(description="Заблокировать")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)
