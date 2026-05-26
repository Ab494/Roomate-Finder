# This file defines the notification models for user alerts and preferences.
# Models handle in-app, SMS, and email notifications for various platform events.

from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class Notification(models.Model):
    """Model for storing individual notifications sent to users."""

    # Types of notifications available
    TYPE_CHOICES = [
        ("match_request", "Match Request"),  # When someone requests to match
        ("match_accepted", "Match Accepted"),  # When a match is accepted
        ("new_message", "New Message"),  # When a new chat message arrives
        ("review", "New Review"),  # When user receives a review
        ("listing", "Listing Update"),  # When listing status changes
        ("system", "System"),  # System announcements
    ]
    # Channels through which notifications can be sent
    CHANNEL_CHOICES = [
        ("in_app", "In App"),  # Show in the app interface
        ("sms", "SMS"),  # Send via text message
        ("email", "Email"),  # Send via email
        ("both", "SMS + Email"),  # Send via both SMS and email
    ]

    # User who should receive this notification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    # Type of notification
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="system")
    # Channel to use for delivery
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES, default="in_app")
    # Notification message content
    message = models.TextField()
    # Whether user has read this notification
    is_read = models.BooleanField(default=False)
    # Timestamp when notification was sent
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"  # Database table name
        ordering = ["-sent_at"]  # Order by most recent first

    def __str__(self):
        # String representation showing type and recipient
        return f"[{self.type}] → {self.user.email}"


class NotificationPreference(models.Model):
    """Model for storing user preferences for how different notification types are delivered."""

    # User these preferences belong to (one-to-one relationship)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="notification_prefs")
    # Preferred channel for match notifications
    match_channel = models.CharField(max_length=10, default="both")
    # Preferred channel for message notifications
    message_channel = models.CharField(max_length=10, default="in_app")
    # Preferred channel for review notifications
    review_channel = models.CharField(max_length=10, default="in_app")
    # Preferred channel for system notifications
    system_channel = models.CharField(max_length=10, default="in_app")

    class Meta:
        db_table = "notification_preferences"  # Database table name

    def __str__(self):
        # String representation showing user
        return f"Notification prefs for {self.user.email}"
