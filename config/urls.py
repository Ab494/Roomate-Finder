from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Health check — used by Render, Docker, and uptime monitors
    path("api/health/", include("apps.health.urls")),

    # API docs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # App endpoints
    path("api/auth/", include("apps.profiles.urls.auth")),
    path("api/profiles/", include("apps.profiles.urls.profiles")),
    path("api/listings/", include("apps.listings.urls")),
    path("api/matches/", include("apps.matching.urls")),
    path("api/conversations/", include("apps.messaging.urls")),
    path("api/reviews/", include("apps.reviews.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/admin/", include("apps.adminpanel.urls")),
]
