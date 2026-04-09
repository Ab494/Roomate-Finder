from rest_framework import serializers
from apps.profiles.serializers import ProfileSerializer
from .models import Match


class MatchSerializer(serializers.ModelSerializer):
    user_a_profile = ProfileSerializer(source='user_a.profile', read_only=True)
    user_b_profile = ProfileSerializer(source='user_b.profile', read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'user_a', 'user_b', 'user_a_profile', 'user_b_profile',
            'listing', 'score', 'score_breakdown', 'status', 'matched_at',
        ]
        read_only_fields = ['id', 'score', 'score_breakdown', 'matched_at']


class MatchSuggestionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    score = serializers.FloatField()
    breakdown = serializers.DictField()
    profile = serializers.SerializerMethodField()

    def get_profile(self, obj):
        from django.contrib.auth import get_user_model
        from apps.profiles.serializers import ProfileSerializer
        User = get_user_model()
        try:
            user = User.objects.select_related('profile').get(pk=obj['user_id'])
            return ProfileSerializer(user.profile).data
        except Exception:
            return None


class MatchRequestSerializer(serializers.Serializer):
    target_user_id = serializers.IntegerField()
    listing_id = serializers.IntegerField(required=False, allow_null=True)
