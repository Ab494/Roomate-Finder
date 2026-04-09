from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.permissions import IsOwnerOrReadOnly
from core.utils import haversine_distance
from .models import Listing, ListingPhoto
from .serializers import (
    ListingSerializer, ListingCreateSerializer, ListingPhotoUploadSerializer
)
from .filters import ListingFilter


class ListingListCreateView(generics.ListCreateAPIView):
    filterset_class = ListingFilter
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'city', 'area']
    ordering_fields = ['rent', 'created_at', 'views_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return Listing.objects.filter(
            status='active', is_approved=True
        ).select_related('owner__profile').prefetch_related('photos')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Listing.objects.select_related('owner__profile').prefetch_related('photos')
    permission_classes = [IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListingCreateSerializer
        return ListingSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        return Response(ListingSerializer(instance).data)


class MyListingsView(generics.ListAPIView):
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(
            owner=self.request.user
        ).prefetch_related('photos')


class ListingPhotoUploadView(APIView):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk, owner=request.user)
        serializer = ListingPhotoUploadSerializer(
            data=request.data, context={'listing': listing}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NearbyListingsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lng = float(request.query_params.get('lng'))
            radius = float(request.query_params.get('radius', 10))
        except (TypeError, ValueError):
            return Response({'error': 'lat, lng, and optional radius are required'}, status=400)

        listings = Listing.objects.filter(
            status='active', is_approved=True,
            lat__isnull=False, lng__isnull=False
        ).select_related('owner__profile').prefetch_related('photos')

        nearby = []
        for listing in listings:
            dist = haversine_distance(lat, lng, listing.lat, listing.lng)
            if dist <= radius:
                data = ListingSerializer(listing).data
                data['distance_km'] = round(dist, 2)
                nearby.append(data)

        nearby.sort(key=lambda x: x['distance_km'])
        return Response({'count': len(nearby), 'results': nearby})
