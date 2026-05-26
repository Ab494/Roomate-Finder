# This file defines the data models for room listings in the Roommate Finder app.
# Models represent database tables for storing room listing information.

from django.contrib.auth import get_user_model
from django.db import models

# Get the custom User model
User = get_user_model()


# Listing model represents a room or apartment listing
class Listing(models.Model):
    # Choices for furnishing status
    FURNISHED_CHOICES = [
        ("furnished", "Fully Furnished"),  # Room comes with furniture
        ("semi", "Semi Furnished"),  # Some furniture provided
        ("unfurnished", "Unfurnished"),  # No furniture provided
    ]
    # Choices for listing status
    STATUS_CHOICES = [
        ("active", "Active"),  # Listing is visible and available
        ("taken", "Taken"),  # Room has been rented
        ("paused", "Paused"),  # Listing temporarily paused
    ]

    # Basic listing information
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")  # User who created the listing
    title = models.CharField(max_length=200)  # Title of the listing
    description = models.TextField()  # Detailed description
    rent = models.PositiveIntegerField(help_text="Monthly rent in KES")  # Monthly rent amount
    rooms_available = models.PositiveIntegerField(default=1)  # Number of rooms available
    furnished = models.CharField(max_length=15, choices=FURNISHED_CHOICES, default="unfurnished")  # Furnishing status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")  # Current status of listing

    # Location information
    city = models.CharField(max_length=100)  # City where the property is located
    area = models.CharField(max_length=100)  # Specific area/neighborhood
    address = models.CharField(max_length=255, blank=True)  # Full address (optional)
    lat = models.FloatField(null=True, blank=True)  # Latitude coordinate for mapping
    lng = models.FloatField(null=True, blank=True)  # Longitude coordinate for mapping

    # Amenities available at the property
    has_wifi = models.BooleanField(default=False)  # Internet access
    has_parking = models.BooleanField(default=False)  # Parking space
    has_gym = models.BooleanField(default=False)  # Gym access
    has_pool = models.BooleanField(default=False)  # Swimming pool
    has_security = models.BooleanField(default=False)  # Security services
    water_included = models.BooleanField(default=False)  # Water bill included in rent
    electricity_included = models.BooleanField(default=False)  # Electricity bill included in rent

    # Preferences for potential roommates
    preferred_gender = models.CharField(max_length=10, default="any")  # Preferred gender of roommate
    smoking_allowed = models.BooleanField(default=False)  # Whether smoking is allowed
    pets_allowed = models.BooleanField(default=False)  # Whether pets are allowed
    guests_allowed = models.BooleanField(default=True)  # Whether guests are allowed

    # Administrative flags
    is_flagged = models.BooleanField(default=False)  # Whether listing has been flagged for review
    is_approved = models.BooleanField(default=True)  # Whether listing is approved for display
    views_count = models.PositiveIntegerField(default=0)  # Number of times listing has been viewed

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # When listing was created
    updated_at = models.DateTimeField(auto_now=True)  # When listing was last updated

    class Meta:
        db_table = "listings"  # Database table name
        ordering = ["-created_at"]  # Order by creation date, newest first

    def __str__(self):
        return f"{self.title} — {self.city} ({self.rent} KES)"  # String representation


# Model for photos associated with listings
class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos")  # Associated listing
    image = models.ImageField(upload_to="listings/")  # Image file stored in listings/ directory
    is_cover = models.BooleanField(default=False)  # Whether this is the cover photo for the listing
    uploaded_at = models.DateTimeField(auto_now_add=True)  # When photo was uploaded

    class Meta:
        db_table = "listing_photos"  # Database table name

    def __str__(self):
        return f"Photo for {self.listing.title}"  # String representation
