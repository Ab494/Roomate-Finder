# URL patterns for authentication endpoints.
# Handles user registration, login, logout, and password management.

from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.profiles.views import ChangePasswordView, LogoutView, RegisterView

urlpatterns = [
    # User registration endpoint
    path("register/", RegisterView.as_view(), name="auth-register"),
    # JWT token obtain (login) endpoint
    path("login/", TokenObtainPairView.as_view(), name="auth-login"),
    # JWT token refresh endpoint
    path("token/refresh/", TokenRefreshView.as_view(), name="auth-token-refresh"),
    # User logout endpoint (blacklists refresh token)
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    # Password change endpoint
    path("change-password/", ChangePasswordView.as_view(), name="auth-change-password"),
]
