from django.contrib import admin
from .models import Listing, ListingPhoto


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "city", "rent", "status", "is_approved", "is_flagged"]
    list_filter = ["status", "is_approved", "is_flagged", "furnished"]
    search_fields = ["title", "city", "area", "owner__email"]
    actions = ["approve_listings", "flag_listings"]

    def approve_listings(self, request, queryset):
        queryset.update(is_approved=True)

    def flag_listings(self, request, queryset):
        queryset.update(is_flagged=True)


admin.site.register(ListingPhoto)
