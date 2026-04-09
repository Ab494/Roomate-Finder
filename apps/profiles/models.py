from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# This file defines the data models for user profiles in the Roommate Finder app.
# Models represent database tables and define the structure of data stored.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# Custom User model that extends Django's built-in AbstractUser
# This allows us to add extra fields specific to our roommate finder app
class User(AbstractUser):
    # Define choices for user roles in the platform
    SEEKER = 'seeker'  # User looking for roommates
    LISTER = 'lister'  # User listing rooms
    BOTH = 'both'     # User doing both
    ROLE_CHOICES = [
        (SEEKER, 'Roommate Seeker'),
        (LISTER, 'Room Lister'),
        (BOTH, 'Both'),
    ]

    # Verification status for user accounts
    UNVERIFIED = 'unverified'
    PENDING = 'pending'
    VERIFIED = 'verified'
    VERIFICATION_CHOICES = [
        (UNVERIFIED, 'Unverified'),
        (PENDING, 'Pending Verification'),
        (VERIFIED, 'Verified'),
    ]

    # Reasons why a user might be banned
    SPAM = 'spam'
    HARASSMENT = 'harassment'
    FRAUD = 'fraud'
    OTHER = 'other'
    BAN_CHOICES = [
        (SPAM, 'Spam'),
        (HARASSMENT, 'Harassment'),
        (FRAUD, 'Fraud'),
        (OTHER, 'Other'),
    ]

    # Additional fields for our custom user model
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=SEEKER)  # User's role on platform
    verification_status = models.CharField(max_length=12, choices=VERIFICATION_CHOICES, default=UNVERIFIED)  # Account verification status
    is_banned = models.BooleanField(default=False)  # Whether user is banned
    ban_reason = models.CharField(max_length=15, choices=BAN_CHOICES, blank=True)  # Reason for ban
    banned_at = models.DateTimeField(null=True, blank=True)  # When user was banned
    banned_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # Admin who banned user
    average_rating = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)])  # User's average rating from reviews
    total_reviews = models.PositiveIntegerField(default=0)  # Total number of reviews received

    class Meta:
        db_table = 'users'  # Database table name

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"  # String representation of user


# Profile model contains additional user information beyond basic auth
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')  # Link to User model
    first_name = models.CharField(max_length=50)  # User's first name
    last_name = models.CharField(max_length=50)  # User's last name
    phone = models.CharField(max_length=15, blank=True)  # Phone number
    bio = models.TextField(blank=True)  # User's biography/description
    date_of_birth = models.DateField(null=True, blank=True)  # Birth date
    occupation = models.CharField(max_length=100, blank=True)  # Job/occupation
    # Location information
    city = models.CharField(max_length=100)  # City of residence
    area = models.CharField(max_length=100)  # Specific area/neighborhood
    lat = models.FloatField(null=True, blank=True)  # Latitude coordinate
    lng = models.FloatField(null=True, blank=True)  # Longitude coordinate
    # Media files
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)  # Profile photo
    # Social media links
    facebook = models.URLField(blank=True)  # Facebook profile URL
    twitter = models.URLField(blank=True)   # Twitter profile URL
    instagram = models.URLField(blank=True) # Instagram profile URL
    # Verification documents
    id_document = models.ImageField(upload_to='verification/', blank=True)  # ID for verification
    # Status flags
    is_verified = models.BooleanField(default=False)  # Whether profile is verified
    is_complete = models.BooleanField(default=False)  # Whether profile is fully filled out
    created_at = models.DateTimeField(auto_now_add=True)  # When profile was created
    updated_at = models.DateTimeField(auto_now=True)     # When profile was last updated

    class Meta:
        db_table = 'profiles'  # Database table name
        ordering = ['-created_at']  # Default ordering by creation date (newest first)

    @property
    def full_name(self):
        # Property to get user's full name by combining first and last name
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} — {self.city}"  # String representation


# Preference model stores user's roommate preferences
class Preference(models.Model):
    # Define choices for gender preferences
    MALE = 'male'
    FEMALE = 'female'
    ANY = 'any'
    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (ANY, 'Any'),
    ]

    # Define choices for sleep schedule preferences
    EARLY_BIRD = 'early'    # Goes to bed early, wakes early
    NIGHT_OWL = 'night'     # Stays up late, wakes late
    FLEXIBLE = 'flexible'   # Flexible sleep schedule
    SLEEP_CHOICES = [
        (EARLY_BIRD, 'Early Bird'),
        (NIGHT_OWL, 'Night Owl'),
        (FLEXIBLE, 'Flexible'),
    ]

    # Define choices for cleanliness preferences
    VERY_CLEAN = 'very_clean'
    CLEAN = 'clean'
    MODERATE = 'moderate'
    MESSY = 'messy'
    CLEANLINESS_CHOICES = [
        (VERY_CLEAN, 'Very Clean'),
        (CLEAN, 'Clean'),
        (MODERATE, 'Moderate'),
        (MESSY, 'Messy'),
    ]

    # Define choices for noise tolerance
    QUIET = 'quiet'
    MODERATE_NOISE = 'moderate'
    LOUD = 'loud'
    NOISE_CHOICES = [
        (QUIET, 'Quiet'),
        (MODERATE_NOISE, 'Moderate Noise'),
        (LOUD, 'Loud'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')  # Link to User
    # Budget preferences
    min_budget = models.PositiveIntegerField(default=0, help_text='Minimum monthly budget in KES')  # Min rent willing to pay
    max_budget = models.PositiveIntegerField(default=50000, help_text='Maximum monthly budget in KES')  # Max rent willing to pay
    # Roommate preferences
    preferred_gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default=ANY)  # Preferred gender of roommate
    preferred_age_min = models.PositiveIntegerField(default=18)  # Minimum preferred age
    preferred_age_max = models.PositiveIntegerField(default=65)  # Maximum preferred age
    sleep_schedule = models.CharField(max_length=10, choices=SLEEP_CHOICES, default=FLEXIBLE)  # Preferred sleep habits
    cleanliness = models.CharField(max_length=15, choices=CLEANLINESS_CHOICES, default=MODERATE)  # Preferred cleanliness level
    noise_tolerance = models.CharField(max_length=10, choices=NOISE_CHOICES, default=MODERATE_NOISE)  # Preferred noise level
    # Boolean preferences
    smoking_ok = models.BooleanField(default=False)  # OK with smoking roommates
    pets_ok = models.BooleanField(default=False)    # OK with pet-owning roommates
    guests_ok = models.BooleanField(default=True)   # OK with guests visiting
    # Location preferences
    max_distance_km = models.PositiveIntegerField(default=10, help_text='Maximum distance from preferred area in km')  # Max distance from preferred areas
    preferred_areas = models.JSONField(default=list, help_text='List of preferred area IDs')  # List of preferred location IDs
    created_at = models.DateTimeField(auto_now_add=True)  # When preferences were created
    updated_at = models.DateTimeField(auto_now=True)     # When preferences were last updated

    class Meta:
        db_table = 'preferences'  # Database table name
        ordering = ['-created_at']  # Default ordering

    def __str__(self):
        return f"Preferences for {self.user.email}"  # String representation
