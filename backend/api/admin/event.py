from django.contrib import admin

from api.models import Event


# @admin.register(models.Event)
# class EventAdmin(admin.ModelAdmin):
#     list_display = [
#         "title",
#         "notifications",
#         "city",
#         "date",
#         "start_time",
#         "end_time",
#         "theme",
#         "get_categories",
#         "cover",
#         "location_name",
#         "location_address",
#         "stats_men",
#         "stats_women",
#         "short_description",
#         "min_age",
#         "max_age",
#         "organizer",
#         "will_come",
#     ]

#     def location_name(self, obj):
#         return obj.location.name

#     def location_address(self, obj):
#         return obj.location.address

#     def will_come(self, obj):
#         return obj.participants.user
