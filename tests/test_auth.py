import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, ProfileFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
class TestAuth:
    def test_register(self, client):
        response = client.post('/api/auth/register/', {
            'email': 'jane@test.com',
            'phone': '+254712345678',
            'role': 'seeker',
            'password': 'securepass123',
            'full_name': 'Jane Wanjiku',
        })
        assert response.status_code == 201
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == 'jane@test.com'

    def test_register_duplicate_email(self, client):
        UserFactory(email='taken@test.com')
        response = client.post('/api/auth/register/', {
            'email': 'taken@test.com',
            'password': 'pass12345',
            'full_name': 'Someone',
        })
        assert response.status_code == 400

    def test_login(self, client):
        user = UserFactory(email='login@test.com')
        user.set_password('mypassword')
        user.save()
        response = client.post('/api/auth/login/', {
            'email': 'login@test.com',
            'password': 'mypassword',
        })
        assert response.status_code == 200
        assert 'access' in response.data

    def test_login_wrong_password(self, client):
        UserFactory(email='user@test.com')
        response = client.post('/api/auth/login/', {
            'email': 'user@test.com',
            'password': 'wrongpassword',
        })
        assert response.status_code == 401

    def test_get_own_profile_authenticated(self, client):
        user = UserFactory()
        ProfileFactory(user=user)
        client.force_authenticate(user=user)
        response = client.get('/api/profiles/me/')
        assert response.status_code == 200
        assert response.data['email'] == user.email

    def test_get_profile_unauthenticated(self, client):
        response = client.get('/api/profiles/me/')
        assert response.status_code == 401

    def test_update_location(self, client):
        user = UserFactory()
        ProfileFactory(user=user)
        client.force_authenticate(user=user)
        response = client.put('/api/profiles/location/', {
            'lat': -1.2921,
            'lng': 36.8219,
            'city': 'Nairobi',
            'area': 'CBD',
        })
        assert response.status_code == 200
        assert response.data['lat'] == -1.2921
