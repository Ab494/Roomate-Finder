# This file defines the matching models for roommate compatibility.
# Models store compatibility matches between users, optionally tied to specific listings.

from django.contrib.auth import get_user_model
from django.db import models

from apps.listings.models import Listing

# Get the custom User model
User = get_user_model()


class Match(models.Model):
    """Model representing a compatibility match between two users."""

    # Possible statuses for a match
    STATUS_CHOICES = [
        ("pending", "Pending"),  # Match suggested, no action taken
        ("accepted", "Accepted"),  # Match accepted by users
        ("declined", "Declined"),  # Match declined by users
    ]

    # First user in the match (order doesn't matter)
    user_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_a")
    # Second user in the match
    user_b = models.ForeignKey(User, on_delete=models.CASCADE, related_name="matches_as_b")
    # Optional listing this match is associated with (for listing-specific matches)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="matches", null=True, blank=True)
    # Compatibility score from 0-100
    score = models.FloatField(default=0.0, help_text="Compatibility score 0-100")
    # Current status of the match
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    # Detailed breakdown of how the score was calculated
    score_breakdown = models.JSONField(default=dict)
    # Timestamp when match was created
    matched_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when match was last updated
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "matches"  # Database table name
        unique_together = [["user_a", "user_b", "listing"]]  # Prevent duplicate matches for same users/listing
        ordering = ["-score"]  # Order by highest score first

    def __str__(self):
        # String representation showing both users and score
        return f"{self.user_a.email} ↔ {self.user_b.email} ({self.score:.1f})"
