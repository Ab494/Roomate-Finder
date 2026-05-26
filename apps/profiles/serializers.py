# This file contains Django REST Framework serializers for user profiles.
# Serializers handle data validation, conversion, and API response formatting.

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Preference, Profile

# Get the custom User model
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    # Password field with minimum length validation
    password = serializers.CharField(write_only=True, min_length=8)
    # Full name field for registration (stored in Profile)
    full_name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "phone", "role", "password", "full_name"]

    def create(self, validated_data):
        """Create user and automatically create related Profile and Preference objects."""
        # Extract full_name from validated data (not part of User model)
        full_name = validated_data.pop("full_name")
        # Create user using custom manager
        user = User.objects.create_user(**validated_data)
        # Create related profile with full name
        Profile.objects.create(user=user, full_name=full_name)
        # Create default preferences
        Preference.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information."""

    class Meta:
        model = User
        fields = ["id", "email", "phone", "role", "is_verified", "created_at"]
        # Fields that cannot be modified via API
        read_only_fields = ["id", "is_verified", "created_at"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data with additional computed fields."""

    # Include user email (read-only, accessed via related user)
    email = serializers.EmailField(source="user.email", read_only=True)
    # Include user role (read-only)
    role = serializers.CharField(source="user.role", read_only=True)
    # Computed field for photo URL
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "role",
            "full_name",
            "bio",
            "gender",
            "age",
            "occupation",
            "photo",
            "photo_url",
            "lat",
            "lng",
            "city",
            "area",
            "average_rating",
            "total_reviews",
            "created_at",
        ]
        # Fields that cannot be modified via API
        read_only_fields = ["id", "average_rating", "total_reviews", "created_at"]

    def get_photo_url(self, obj):
        """Return the full URL for the profile photo."""
        if obj.photo:
            return obj.photo.url
        return None


class PreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user roommate preferences."""

    class Meta:
        model = Preference
        # Include all fields except the user field (implicit relationship)
        exclude = ["user"]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change functionality."""

    # Current password for verification
    old_password = serializers.CharField(required=True)
    # New password with minimum length validation
    new_password = serializers.CharField(required=True, min_length=8)
