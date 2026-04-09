from rest_framework import serializers
from .models import Listing, ListingPhoto


class ListingPhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'image_url', 'is_cover', 'uploaded_at']

    def get_image_url(self, obj):
        return obj.image.url if obj.image else None


class ListingSerializer(serializers.ModelSerializer):
    photos = ListingPhotoSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.profile.full_name', read_only=True)
    owner_photo = serializers.SerializerMethodField()
    owner_rating = serializers.FloatField(source='owner.profile.average_rating', read_only=True)

    class Meta:
        model = Listing
        fields = [
            'id', 'owner', 'owner_name', 'owner_photo', 'owner_rating',
            'title', 'description', 'rent', 'rooms_available', 'furnished', 'status',
            'city', 'area', 'address', 'lat', 'lng',
            'has_wifi', 'has_parking', 'has_gym', 'has_pool', 'has_security',
            'water_included', 'electricity_included',
            'preferred_gender', 'smoking_allowed', 'pets_allowed', 'guests_allowed',
            'views_count', 'photos', 'created_at',
        ]
        read_only_fields = ['id', 'owner', 'views_count', 'created_at']

    def get_owner_photo(self, obj):
        try:
            photo = obj.owner.profile.photo
            return photo.url if photo else None
        except Exception:
            return None


class ListingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        exclude = ['owner', 'views_count', 'is_flagged', 'is_approved', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ListingPhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingPhoto
        fields = ['id', 'image', 'is_cover']

    def create(self, validated_data):
        listing = self.context['listing']
        if validated_data.get('is_cover'):
            listing.photos.filter(is_cover=True).update(is_cover=False)
        return ListingPhoto.objects.create(listing=listing, **validated_data)
