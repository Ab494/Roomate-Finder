"""
Roommate compatibility scoring engine.

This module calculates compatibility scores between potential roommates based on:
- Budget compatibility
- Gender preferences
- Lifestyle matches (sleep, cleanliness, noise)
- Geographic proximity
- Lifestyle boolean preferences (smoking, pets, guests)

Weights (total = 100 pts):
  Budget overlap      25 pts
  Gender preference   20 pts
  Lifestyle           25 pts  (sleep 10, cleanliness 8, noise 7)
  Location proximity  20 pts
  Booleans            10 pts  (smoking 4, pets 3, guests 3)
"""

from core.utils import haversine_distance


def _budget_score(pref_a, pref_b):
    """Calculate compatibility score based on overlapping budget ranges."""
    # Find the overlap between the two budget ranges
    lo = max(pref_a.min_budget, pref_b.min_budget)  # Highest minimum budget
    hi = min(pref_a.max_budget, pref_b.max_budget)  # Lowest maximum budget
    if hi < lo:
        return 0.0  # No overlap, complete mismatch

    # Calculate overlap and normalize by the smaller range
    overlap = hi - lo
    range_a = max(pref_a.max_budget - pref_a.min_budget, 1)
    range_b = max(pref_b.max_budget - pref_b.min_budget, 1)
    ratio = overlap / min(range_a, range_b)

    # Return score out of 25 points, capped at 1.0 ratio
    return round(min(ratio, 1.0) * 25, 2)


def _gender_score(pref_a, profile_b, pref_b, profile_a):
    """Calculate score based on mutual gender preferences."""

    def _ok(pref, profile):
        # Check if preference accepts the profile's gender
        if pref.preferred_gender == "any":
            return True  # Accepts any gender
        return pref.preferred_gender == profile.user.role

    # Both mutually acceptable = full 20 points
    if _ok(pref_a, profile_b) and _ok(pref_b, profile_a):
        return 20.0
    # One-way acceptable = partial 10 points
    if _ok(pref_a, profile_b) or _ok(pref_b, profile_a):
        return 10.0
    # Neither acceptable = 0 points
    return 0.0


def _lifestyle_score(pref_a, pref_b):
    """Calculate lifestyle compatibility score across multiple factors."""
    score = 0.0

    # Sleep schedule compatibility (10 pts)
    if pref_a.sleep_schedule == pref_b.sleep_schedule:
        score += 10.0  # Perfect match
    elif "flexible" in (pref_a.sleep_schedule, pref_b.sleep_schedule):
        score += 7.0  # Partial match if one is flexible

    # Cleanliness compatibility (8 pts)
    # Map cleanliness levels to numeric values for comparison
    levels = {"very_clean": 3, "clean": 2, "relaxed": 1}
    diff = abs(levels.get(pref_a.cleanliness, 2) - levels.get(pref_b.cleanliness, 2))
    score += max(0, 8 - diff * 4)  # Reduce score based on difference

    # Noise level compatibility (7 pts)
    noise_levels = {"quiet": 1, "moderate": 2, "loud": 3}
    diff = abs(noise_levels.get(pref_a.noise_tolerance, 2) - noise_levels.get(pref_b.noise_tolerance, 2))
    score += max(0, 7 - diff * 3.5)  # Reduce score based on difference

    return round(score, 2)


def _location_score(profile_a, profile_b, pref_a, pref_b):
    """Calculate score based on geographic proximity between users."""
    # If location data is missing, return neutral score
    if not all([profile_a.lat, profile_a.lng, profile_b.lat, profile_b.lng]):
        return 10.0

    # Calculate distance using Haversine formula
    dist = haversine_distance(profile_a.lat, profile_a.lng, profile_b.lat, profile_b.lng)

    # Use the more restrictive distance preference
    max_dist = min(
        pref_a.max_distance_km or 20,
        pref_b.max_distance_km or 20,
    )

    # Scoring based on distance
    if dist <= 2:
        return 20.0  # Very close, full points
    if dist > max_dist:
        return 0.0  # Too far, no points

    # Linear score reduction based on distance ratio
    ratio = 1 - (dist / max_dist)
    return round(ratio * 20, 2)


def _boolean_score(pref_a, pref_b):
    """Calculate score based on matching boolean lifestyle preferences."""
    score = 0.0

    # Smoking compatibility (4 pts) - both must agree
    if pref_a.smoking_ok == pref_b.smoking_ok:
        score += 4.0

    # Pets compatibility (3 pts)
    if pref_a.pets_ok == pref_b.pets_ok:
        score += 3.0

    # Guests compatibility (3 pts)
    if pref_a.guests_ok == pref_b.guests_ok:
        score += 3.0

    return score


def compute_compatibility(user_a, user_b):
    """
    Compute full compatibility score between two users.

    Args:
        user_a: First user object
        user_b: Second user object

    Returns:
        tuple: (total_score, breakdown_dict) where breakdown contains
               individual component scores
    """
    try:
        # Get related profile and preference data
        profile_a = user_a.profile
        profile_b = user_b.profile
        pref_a = user_a.preferences
        pref_b = user_b.preferences
    except Exception:
        # Return zero score if data is missing
        return 0.0, {}

    # Calculate individual component scores
    budget = _budget_score(pref_a, pref_b)
    gender = _gender_score(pref_a, profile_b, pref_b, profile_a)
    lifestyle = _lifestyle_score(pref_a, pref_b)
    location = _location_score(profile_a, profile_b, pref_a, pref_b)
    booleans = _boolean_score(pref_a, pref_b)

    # Sum all components for total score
    total = round(budget + gender + lifestyle + location + booleans, 2)

    # Return total and detailed breakdown
    breakdown = {
        "budget": budget,
        "gender": gender,
        "lifestyle": lifestyle,
        "location": location,
        "booleans": booleans,
        "total": total,
    }
    return total, breakdown
