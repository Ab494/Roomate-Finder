from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Preference, Profile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True, required=False, default="")

    class Meta:
        model = User
        fields = ["email", "username", "role", "password", "first_name", "last_name"]

    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name", "")
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, first_name=first_name, last_name=last_name)
        Preference.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information."""

    class Meta:
        model = User
        fields = ["id", "email", "username", "role", "verification_status", "date_joined"]
        read_only_fields = ["id", "verification_status", "date_joined"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data."""

    email = serializers.EmailField(source="user.email", read_only=True)
    role = serializers.CharField(source="user.role", read_only=True)
    full_name = serializers.CharField(read_only=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "role",
            "full_name",
            "first_name",
            "last_name",
            "bio",
            "occupation",
            "profile_picture",
            "photo_url",
            "lat",
            "lng",
            "city",
            "area",
            "is_verified",
            "is_complete",
            "created_at",
        ]
        read_only_fields = ["id", "is_verified", "created_at"]

    def get_photo_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None


class PreferenceSerializer(serializers.ModelSerializer):
    """Serializer for user roommate preferences."""

    class Meta:
        model = Preference
        exclude = ["user"]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
