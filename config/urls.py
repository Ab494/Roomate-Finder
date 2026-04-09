# Main URL configuration for the Roommate Finder Django project.
# This file defines all URL patterns and includes API documentation routes.

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Django admin interface for platform administrators
    path('admin/', admin.site.urls),

    # API documentation routes (OpenAPI/Swagger)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),  # Raw OpenAPI schema
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # Swagger UI
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # ReDoc UI

    # API endpoints for different app functionalities
    path('api/auth/', include('apps.profiles.urls.auth')),      # Authentication (login/register)
    path('api/profiles/', include('apps.profiles.urls.profiles')),  # User profiles
    path('api/listings/', include('apps.listings.urls')),      # Room listings
    path('api/matches/', include('apps.matching.urls')),       # Roommate matches
    path('api/conversations/', include('apps.messaging.urls')), # Chat conversations
    path('api/reviews/', include('apps.reviews.urls')),        # User reviews
    path('api/notifications/', include('apps.notifications.urls')), # Notifications
    path('api/admin/', include('apps.adminpanel.urls')),       # Admin panel
]
