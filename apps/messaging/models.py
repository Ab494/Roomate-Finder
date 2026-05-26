# This file defines the messaging models for real-time chat functionality.
# Models handle conversations between users and message storage.

from django.db import models
from django.contrib.auth import get_user_model

# Get the custom User model
User = get_user_model()


class Conversation(models.Model):
    """Model representing a chat conversation between multiple users."""

    # Users participating in this conversation (many-to-many relationship)
    participants = models.ManyToManyField(User, related_name="conversations")
    # Timestamp when conversation was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when conversation was last updated (new message)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "conversations"  # Database table name
        ordering = ["-updated_at"]  # Order by most recently updated first

    def get_other_participant(self, user):
        """Get the other participant in a two-person conversation."""
        return self.participants.exclude(pk=user.pk).first()

    def __str__(self):
        # String representation showing conversation ID
        return f"Conversation #{self.pk}"


class Message(models.Model):
    """Model representing individual messages within a conversation."""

    # Conversation this message belongs to
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    # User who sent the message
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    # Text content of the message
    content = models.TextField()
    # Whether the message has been read by recipients
    is_read = models.BooleanField(default=False)
    # Timestamp when message was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "messages"  # Database table name
        ordering = ["created_at"]  # Order messages chronologically

    def __str__(self):
        # String representation showing sender and conversation
        return f"Message from {self.sender.email} in #{self.conversation.pk}"
