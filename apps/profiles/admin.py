from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Preference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'role', 'is_verified', 'is_banned', 'created_at']
    list_filter = ['role', 'is_verified', 'is_banned', 'is_staff']
    search_fields = ['email', 'phone']
    ordering = ['-created_at']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Info', {'fields': ('phone', 'role')}),
        ('Status', {'fields': ('is_active', 'is_verified', 'is_banned', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'phone', 'role', 'password1', 'password2')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'city', 'average_rating']
    search_fields = ['full_name', 'city', 'user__email']


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'min_budget', 'max_budget', 'gender_preference']
