# Django app configuration for the profiles app.
# This class handles app-specific settings and initialization.

from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    # Use BigAutoField for primary keys (handles large datasets)
    default_auto_field = "django.db.models.BigAutoField"
    # App module path
    name = "apps.profiles"
