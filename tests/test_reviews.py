import pytest
from rest_framework.test import APIClient
from tests.factories import UserFactory, ProfileFactory, ReviewFactory


@pytest.mark.django_db
class TestReviews:
    def setup_method(self):
        self.client = APIClient()
        self.reviewer = UserFactory()
        self.reviewee = UserFactory()
        ProfileFactory(user=self.reviewer)
        ProfileFactory(user=self.reviewee)
        self.client.force_authenticate(user=self.reviewer)

    def test_create_review(self):
        response = self.client.post('/api/reviews/', {
            'reviewee': self.reviewee.pk,
            'rating': 5,
            'comment': 'Great roommate, very clean!',
        })
        assert response.status_code == 201
        assert response.data['rating'] == 5

    def test_cannot_review_self(self):
        response = self.client.post('/api/reviews/', {
            'reviewee': self.reviewer.pk,
            'rating': 5,
        })
        assert response.status_code == 400

    def test_cannot_review_twice(self):
        ReviewFactory(reviewer=self.reviewer, reviewee=self.reviewee)
        response = self.client.post('/api/reviews/', {
            'reviewee': self.reviewee.pk,
            'rating': 3,
        })
        assert response.status_code == 400

    def test_average_rating_updated(self):
        ReviewFactory(reviewer=self.reviewer, reviewee=self.reviewee, rating=4)
        other_reviewer = UserFactory()
        ProfileFactory(user=other_reviewer)
        ReviewFactory(reviewer=other_reviewer, reviewee=self.reviewee, rating=2)
        self.reviewee.profile.refresh_from_db()
        assert self.reviewee.profile.average_rating == 3.0
        assert self.reviewee.profile.total_reviews == 2

    def test_get_user_reviews(self):
        ReviewFactory.create_batch(3, reviewee=self.reviewee)
        response = self.client.get(f'/api/reviews/user/{self.reviewee.pk}/')
        assert response.status_code == 200
        assert len(response.data['results']) == 3

    def test_report_review(self):
        review = ReviewFactory(reviewee=self.reviewer)
        response = self.client.post(f'/api/reviews/{review.pk}/report/', {
            'reason': 'This review is fake and defamatory',
        })
        assert response.status_code == 200
        review.refresh_from_db()
        assert review.is_reported is True
