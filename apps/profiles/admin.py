from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Preference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "role", "verification_status", "is_banned", "date_joined"]
    list_filter = ["role", "verification_status", "is_banned", "is_staff"]
    search_fields = ["email", "username"]
    ordering = ["-date_joined"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Info", {"fields": ("phone", "role")}),
        ("Status", {"fields": ("is_active", "verification_status", "is_banned", "is_staff", "is_superuser")}),
    )
    add_fieldsets = ((None, {"fields": ("email", "username", "role", "password1", "password2")}),)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "city", "is_verified", "is_complete"]
    search_fields = ["first_name", "last_name", "city", "user__email"]


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ["user", "min_budget", "max_budget", "preferred_gender"]
