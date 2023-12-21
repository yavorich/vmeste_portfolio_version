from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html
from django import forms
from api.models import Category, User


class UserChangeListForm(forms.ModelForm):
    # here we only need to define the field we want to be editable
    interests = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(), required=False
    )


class UserChangeList(ChangeList):
    def __init__(
        self,
        request,
        model,
        list_display,
        list_display_links,
        list_filter,
        date_hierarchy,
        search_fields,
        list_select_related,
        list_per_page,
        list_max_show_all,
        list_editable,
        model_admin,
        sortable_by,
        search_help_text,
    ):
        super(UserChangeList, self).__init__(
            request,
            model,
            list_display,
            list_display_links,
            list_filter,
            date_hierarchy,
            search_fields,
            list_select_related,
            list_per_page,
            list_max_show_all,
            list_editable,
            model_admin,
            sortable_by,
            search_help_text,
        )

        # these need to be defined here, and not in UserAdmin
        list_display = [
            "action_checkbox",
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
            "interests",
            "occupation",
        ]
        self.list_display_links = [
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "country",
        ]
        self.list_editable = self.list_display[2:]


class InterestInline(admin.TabularInline):
    model = User.interests.through


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # def get_changelist(self, request, **kwargs):
    #     return UserChangeList

    # def get_changelist_form(self, request, **kwargs):
    #     return UserChangeListForm

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

    readonly_fields = []
    search_fields = ["first_name", "last_name", "phone_number", "email"]
    actions = ["block_users", "unblock_users"]

    @admin.display(description="Категории")
    def get_interests(self, obj):
        return self.links_to_objects(obj.interests.all())

    @classmethod
    def links_to_objects(cls, objects):
        rel_list = "<ul>"
        for obj in objects:
            link = reverse("admin:api_category_change", args=[obj.id])
            rel_list += "<li><a href='%s'>%s</a></li>" % (link, obj.title)
        rel_list += "</ul>"
        return format_html(rel_list)

    @admin.action(description="Заблокировать")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description="Разблокировать")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)


# admin.site.register(User, UserAdmin)
