from django.contrib import admin

from core.admin import ManyToManyMixin
from api.models import User


# class InterestInline(admin.TabularInline):
#     model = Category


@admin.register(User)
class UserAdmin(ManyToManyMixin, admin.ModelAdmin):
    # inlines = [InterestInline]
    list_display = [
        "is_active",
        "id",
        "phone_number",
        "email",
        "avatar",
        "first_name",
        "last_name",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        "get_interests",
        "occupation",
        "agreement_applied_at",
    ]
    list_display_links = [
        "id",
    ]
    list_editable = [
        "is_active",
        "phone_number",
        "email",
        "avatar",
        "first_name",
        "last_name",
        "gender",
        "country",
        "date_of_birth",
        "telegram",
        "occupation",
        "agreement_applied_at",
    ]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "phone_number",
                    "email",
                    "avatar",
                    "first_name",
                    "last_name",
                    "gender",
                    "country",
                    "date_of_birth",
                    "telegram",
                    "interests",
                    "occupation",
                    "profile_is_completed",
                    "email_is_confirmed",
                    "subscription",
                    "subscription_expires",
                    "agreement_applied_at",
                    "last_login",
                ]
            }
        )
    ]
    readonly_fields = []
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["block_users", "unblock_users"]

    @admin.display(description="Интересы")
    def get_interests(self, obj):
        return self.links_to_objects(obj.interests.all())

    @admin.action(description="Заблокировать")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)
