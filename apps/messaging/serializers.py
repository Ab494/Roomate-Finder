from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.profile.full_name", read_only=True)
    sender_photo = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "conversation", "sender", "sender_name", "sender_photo", "content", "is_read", "created_at"]
        read_only_fields = ["id", "sender", "is_read", "created_at"]

    def get_sender_photo(self, obj):
        try:
            photo = obj.sender.profile.photo
            return photo.url if photo else None
        except Exception:
            return None


class ConversationSerializer(serializers.ModelSerializer):
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "other_participant", "last_message", "unread_count", "updated_at"]

    def get_other_participant(self, obj):
        from apps.profiles.serializers import ProfileSerializer

        user = self.context["request"].user
        other = obj.get_other_participant(user)
        if other and hasattr(other, "profile"):
            return ProfileSerializer(other.profile).data
        return None

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {"content": msg.content, "created_at": msg.created_at, "sender_id": msg.sender_id}
        return None

    def get_unread_count(self, obj):
        user = self.context["request"].user
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class CreateConversationSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField()

    def validate_participant_id(self, value):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not User.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError("User not found")
        return value
