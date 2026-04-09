# This file defines the review models for user ratings and feedback.
# Models handle reviews between users and automatically update profile ratings.

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class Review(models.Model):
    """Model for storing user reviews and ratings with automatic profile updates."""
    # User who wrote the review
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    # User being reviewed
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    # Rating from 1 to 5 stars with validation
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    # Optional text comment
    comment = models.TextField(blank=True)
    # Moderation flags
    is_reported = models.BooleanField(default=False)  # Whether review has been reported
    report_reason = models.TextField(blank=True)     # Reason for reporting
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # When review was created
    updated_at = models.DateTimeField(auto_now=True)     # When review was last updated

    class Meta:
        db_table = 'reviews'  # Database table name
        unique_together = [['reviewer', 'reviewee']]  # One review per reviewer-reviewee pair
        ordering = ['-created_at']  # Order by newest first

    def __str__(self):
        # String representation with star emoji
        return f"{self.reviewer.email} → {self.reviewee.email} ({self.rating}★)"

    def save(self, *args, **kwargs):
        # Save the review and update the reviewee's profile rating
        super().save(*args, **kwargs)
        self._update_reviewee_rating()

    def delete(self, *args, **kwargs):
        # Store reviewee before deletion, then update their rating
        reviewee = self.reviewee
        super().delete(*args, **kwargs)
        self._update_reviewee_rating(reviewee=reviewee)

    def _update_reviewee_rating(self, reviewee=None):
        """Update the reviewee's profile with new average rating and review count."""
        # Get the target user (current reviewee or passed reviewee)
        target = reviewee or self.reviewee
        # Get all reviews for this user
        reviews = Review.objects.filter(reviewee=target)
        # Calculate average rating
        avg = reviews.aggregate(Avg('rating'))['rating__avg'] or 0.0
        try:
            # Update profile with new rating and count
            target.profile.average_rating = round(avg, 1)
            target.profile.total_reviews = reviews.count()
            target.profile.save(update_fields=['average_rating', 'total_reviews'])
        except Exception:
            # Ignore errors (e.g., if profile doesn't exist)
            pass
