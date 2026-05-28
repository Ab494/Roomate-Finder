import pytest

from apps.matching.algorithm import _boolean_score, _budget_score, _lifestyle_score, compute_compatibility
from tests.factories import PreferenceFactory, ProfileFactory, UserFactory


@pytest.mark.django_db
class TestBudgetScore:
    def test_perfect_overlap(self):
        pref_a = PreferenceFactory.build(min_budget=10000, max_budget=20000)
        pref_b = PreferenceFactory.build(min_budget=10000, max_budget=20000)
        assert _budget_score(pref_a, pref_b) == 25.0

    def test_no_overlap(self):
        pref_a = PreferenceFactory.build(min_budget=5000, max_budget=8000)
        pref_b = PreferenceFactory.build(min_budget=30000, max_budget=50000)
        assert _budget_score(pref_a, pref_b) == 0.0

    def test_partial_overlap(self):
        pref_a = PreferenceFactory.build(min_budget=10000, max_budget=20000)
        pref_b = PreferenceFactory.build(min_budget=15000, max_budget=30000)
        score = _budget_score(pref_a, pref_b)
        assert 0 < score < 25


@pytest.mark.django_db
class TestLifestyleScore:
    def test_identical_lifestyle(self):
        pref_a = PreferenceFactory.build(sleep_schedule="early", cleanliness="clean", noise_tolerance="quiet")
        pref_b = PreferenceFactory.build(sleep_schedule="early", cleanliness="clean", noise_tolerance="quiet")
        assert _lifestyle_score(pref_a, pref_b) == 25.0

    def test_opposite_lifestyle(self):
        pref_a = PreferenceFactory.build(sleep_schedule="early", cleanliness="very_clean", noise_tolerance="quiet")
        pref_b = PreferenceFactory.build(sleep_schedule="night", cleanliness="messy", noise_tolerance="loud")
        score = _lifestyle_score(pref_a, pref_b)
        assert score < 10

    def test_flexible_sleep_partial_score(self):
        pref_a = PreferenceFactory.build(sleep_schedule="flexible", cleanliness="clean", noise_tolerance="moderate")
        pref_b = PreferenceFactory.build(sleep_schedule="night", cleanliness="clean", noise_tolerance="moderate")
        score = _lifestyle_score(pref_a, pref_b)
        assert score > 15


@pytest.mark.django_db
class TestBooleanScore:
    def test_all_matching(self):
        pref_a = PreferenceFactory.build(smoking_ok=False, pets_ok=True, guests_ok=True)
        pref_b = PreferenceFactory.build(smoking_ok=False, pets_ok=True, guests_ok=True)
        assert _boolean_score(pref_a, pref_b) == 10.0

    def test_none_matching(self):
        pref_a = PreferenceFactory.build(smoking_ok=True, pets_ok=True, guests_ok=True)
        pref_b = PreferenceFactory.build(smoking_ok=False, pets_ok=False, guests_ok=False)
        assert _boolean_score(pref_a, pref_b) == 0.0


@pytest.mark.django_db
class TestComputeCompatibility:
    def test_compatible_users(self):
        user_a = UserFactory()
        user_b = UserFactory()
        ProfileFactory(user=user_a, lat=-1.28, lng=36.82, city="Nairobi")
        ProfileFactory(user=user_b, lat=-1.29, lng=36.83, city="Nairobi")
        PreferenceFactory(
            user=user_a,
            min_budget=10000,
            max_budget=20000,
            preferred_gender="any",
            sleep_schedule="early",
            cleanliness="clean",
            noise_tolerance="quiet",
            smoking_ok=False,
            pets_ok=False,
            guests_ok=True,
        )
        PreferenceFactory(
            user=user_b,
            min_budget=10000,
            max_budget=20000,
            preferred_gender="any",
            sleep_schedule="early",
            cleanliness="clean",
            noise_tolerance="quiet",
            smoking_ok=False,
            pets_ok=False,
            guests_ok=True,
        )
        score, breakdown = compute_compatibility(user_a, user_b)
        assert score > 70
        assert "budget" in breakdown
        assert "lifestyle" in breakdown
        assert "total" in breakdown

    def test_incompatible_budget_zeroes_score(self):
        user_a = UserFactory()
        user_b = UserFactory()
        ProfileFactory(user=user_a)
        ProfileFactory(user=user_b)
        PreferenceFactory(user=user_a, min_budget=5000, max_budget=8000)
        PreferenceFactory(user=user_b, min_budget=40000, max_budget=80000)
        score, breakdown = compute_compatibility(user_a, user_b)
        assert breakdown["budget"] == 0.0

    def test_missing_profile_returns_zero(self):
        user_a = UserFactory()
        user_b = UserFactory()
        # No profile or preference created
        score, breakdown = compute_compatibility(user_a, user_b)
        assert score == 0.0
