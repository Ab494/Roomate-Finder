from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["reviewer", "reviewee", "rating", "is_reported", "created_at"]
    list_filter = ["rating", "is_reported"]
    search_fields = ["reviewer__email", "reviewee__email", "comment"]
    actions = ["clear_reports"]

    def clear_reports(self, request, queryset):
        queryset.update(is_reported=False, report_reason="")

    clear_reports.short_description = "Clear report flags"
