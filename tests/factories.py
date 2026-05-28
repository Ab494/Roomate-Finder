import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.listings.models import Listing
from apps.matching.models import Match
from apps.profiles.models import Preference, Profile
from apps.reviews.models import Review

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    role = "seeker"
    is_active = True
    verification_status = "verified"

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "testpass123")
        if create:
            obj.save()


class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    bio = factory.Faker("sentence")
    occupation = "Engineer"
    city = "Nairobi"
    area = "Westlands"
    lat = -1.2741
    lng = 36.8038


class PreferenceFactory(DjangoModelFactory):
    class Meta:
        model = Preference

    user = factory.SubFactory(UserFactory)
    min_budget = 10000
    max_budget = 25000
    preferred_gender = "any"
    sleep_schedule = "flexible"
    cleanliness = "clean"
    noise_tolerance = "moderate"
    smoking_ok = False
    pets_ok = False
    guests_ok = True
    max_distance_km = 10


class ListingFactory(DjangoModelFactory):
    class Meta:
        model = Listing

    owner = factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Room {n} in Nairobi")
    description = factory.Faker("paragraph")
    rent = 15000
    rooms_available = 1
    furnished = "furnished"
    city = "Nairobi"
    area = "Kilimani"
    lat = -1.2921
    lng = 36.7821
    status = "active"
    is_approved = True


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    reviewer = factory.SubFactory(UserFactory)
    reviewee = factory.SubFactory(UserFactory)
    rating = 4
    comment = factory.Faker("sentence")


class MatchFactory(DjangoModelFactory):
    class Meta:
        model = Match

    user_a = factory.SubFactory(UserFactory)
    user_b = factory.SubFactory(UserFactory)
    score = 75.0
    status = "pending"
