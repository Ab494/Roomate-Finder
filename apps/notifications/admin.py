from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "channel", "is_read", "sent_at"]
    list_filter = ["type", "channel", "is_read"]
    search_fields = ["user__email", "message"]


admin.site.register(NotificationPreference)
