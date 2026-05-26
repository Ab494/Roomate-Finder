import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, ListingFactory, ProfileFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client():
    client = APIClient()
    user = UserFactory(role="lister")
    ProfileFactory(user=user)
    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
class TestListingCRUD:
    def test_list_listings_public(self, client):
        ListingFactory.create_batch(3)
        response = client.get("/api/listings/")
        assert response.status_code == 200
        assert response.data["count"] == 3

    def test_create_listing_authenticated(self, auth_client):
        client, user = auth_client
        response = client.post(
            "/api/listings/",
            {
                "title": "Cozy bedsitter in Kilimani",
                "description": "Close to Junction Mall, quiet neighborhood",
                "rent": 15000,
                "rooms_available": 1,
                "furnished": "furnished",
                "city": "Nairobi",
                "area": "Kilimani",
            },
        )
        assert response.status_code == 201
        assert response.data["title"] == "Cozy bedsitter in Kilimani"
        assert response.data["rent"] == 15000

    def test_create_listing_unauthenticated(self, client):
        response = client.post("/api/listings/", {"title": "Test"})
        assert response.status_code == 401

    def test_update_listing_owner_only(self, auth_client):
        client, user = auth_client
        listing = ListingFactory(owner=user)
        response = client.patch(f"/api/listings/{listing.pk}/", {"rent": 20000})
        assert response.status_code == 200
        assert response.data["rent"] == 20000

    def test_cannot_update_other_users_listing(self, auth_client):
        client, user = auth_client
        other_listing = ListingFactory()  # Different owner
        response = client.patch(f"/api/listings/{other_listing.pk}/", {"rent": 1})
        assert response.status_code == 403

    def test_filter_by_city(self, client):
        ListingFactory(city="Nairobi")
        ListingFactory(city="Mombasa")
        response = client.get("/api/listings/?city=Nairobi")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_filter_by_rent_range(self, client):
        ListingFactory(rent=10000)
        ListingFactory(rent=25000)
        ListingFactory(rent=50000)
        response = client.get("/api/listings/?min_rent=15000&max_rent=30000")
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_nearby_listings(self, client):
        ListingFactory(lat=-1.28, lng=36.82)  # ~1km from query point
        ListingFactory(lat=-1.50, lng=37.00)  # far away
        response = client.get("/api/listings/nearby/?lat=-1.28&lng=36.82&radius=5")
        assert response.status_code == 200
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestMyListings:
    def test_my_listings_only(self):
        client = APIClient()
        user = UserFactory()
        ProfileFactory(user=user)
        client.force_authenticate(user=user)
        ListingFactory(owner=user)
        ListingFactory(owner=user)
        ListingFactory()  # Another user's listing
        response = client.get("/api/listings/mine/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 2
