# This file contains API views for user authentication, profiles, and preferences.
# It handles registration, login, profile management, and preference settings.

from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Profile, Preference
from .serializers import (
    RegisterSerializer, UserSerializer, ProfileSerializer,
    PreferenceSerializer, ChangePasswordSerializer
)

# Get the custom User model
User = get_user_model()


# ── Authentication Views ────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """API endpoint for user registration."""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]  # Allow unauthenticated access

    def create(self, request, *args, **kwargs):
        # Validate input data using serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create new user
        user = serializer.save()

        # Generate JWT tokens for immediate login
        refresh = RefreshToken.for_user(user)

        # Return user data and access token
        return Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    def post(self, request):
        try:
            token = RefreshToken(request.data['refresh'])
            token.blacklist()
            return Response({'message': 'Logged out successfully'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'error': 'Wrong password'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password updated'})


# ── Profile views ─────────────────────────────────────────────────────────────

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return get_object_or_404(Profile, user=self.request.user)


class PublicProfileView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.select_related('user').all()
    permission_classes = [permissions.AllowAny]


class MyPreferencesView(generics.RetrieveUpdateAPIView):
    serializer_class = PreferenceSerializer

    def get_object(self):
        pref, _ = Preference.objects.get_or_create(user=self.request.user)
        return pref


class UpdateLocationView(APIView):
    def put(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        lat = request.data.get('lat')
        lng = request.data.get('lng')
        city = request.data.get('city', '')
        area = request.data.get('area', '')
        if lat is None or lng is None:
            return Response({'error': 'lat and lng are required'}, status=status.HTTP_400_BAD_REQUEST)
        profile.lat = lat
        profile.lng = lng
        profile.city = city
        profile.area = area
        profile.save()
        return Response({'message': 'Location updated', 'lat': lat, 'lng': lng})
