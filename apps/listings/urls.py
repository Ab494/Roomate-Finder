from django.urls import path
from .views import (
    ListingListCreateView, ListingDetailView, MyListingsView,
    ListingPhotoUploadView, NearbyListingsView,
)

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list'),
    path('mine/', MyListingsView.as_view(), name='listing-mine'),
    path('nearby/', NearbyListingsView.as_view(), name='listing-nearby'),
    path('<int:pk>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<int:pk>/photos/', ListingPhotoUploadView.as_view(), name='listing-photos'),
]
