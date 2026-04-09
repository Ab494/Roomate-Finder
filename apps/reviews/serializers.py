from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source='reviewer.profile.full_name', read_only=True)
    reviewer_photo = serializers.SerializerMethodField()
    reviewee_name = serializers.CharField(source='reviewee.profile.full_name', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewer_name', 'reviewer_photo',
            'reviewee', 'reviewee_name', 'rating', 'comment',
            'is_reported', 'created_at',
        ]
        read_only_fields = ['id', 'reviewer', 'is_reported', 'created_at']

    def get_reviewer_photo(self, obj):
        try:
            photo = obj.reviewer.profile.photo
            return photo.url if photo else None
        except Exception:
            return None

    def validate(self, attrs):
        request = self.context['request']
        reviewee = attrs.get('reviewee')
        if reviewee and reviewee == request.user:
            raise serializers.ValidationError("You cannot review yourself.")
        return attrs


class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['reviewee', 'rating', 'comment']

    def validate(self, attrs):
        request = self.context['request']
        if attrs['reviewee'] == request.user:
            raise serializers.ValidationError("You cannot review yourself.")
        if Review.objects.filter(reviewer=request.user, reviewee=attrs['reviewee']).exists():
            raise serializers.ValidationError("You have already reviewed this user.")
        return attrs

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return super().create(validated_data)


class ReportReviewSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=500)
