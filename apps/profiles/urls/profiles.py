# URL patterns for profile-related endpoints.
# Handles profile viewing, editing, preferences, and location updates.

from django.urls import path

from .. import views

urlpatterns = [
    # Current user's profile (view/edit)
    path("me/", views.MyProfileView.as_view(), name="my-profile"),
    # Public profile view (read-only)
    path("public/<int:pk>/", views.PublicProfileView.as_view(), name="public-profile"),
    # User's roommate preferences
    path("preferences/", views.MyPreferencesView.as_view(), name="my-preferences"),
    # Update location coordinates
    path("location/", views.UpdateLocationView.as_view(), name="update-location"),
]
