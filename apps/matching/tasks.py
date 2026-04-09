from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

SUGGESTIONS_CACHE_TTL = 60 * 30  # 30 minutes


@shared_task(bind=True, max_retries=3)
def compute_matches_for_user(self, user_id):
    """
    Compute compatibility scores between this user and all others.
    Stores top 20 matches in Redis cache.
    """
    from .algorithm import compute_compatibility
    from .models import Match

    try:
        user = User.objects.select_related('profile', 'preferences').get(pk=user_id)
    except User.DoesNotExist:
        return

    candidates = User.objects.exclude(pk=user_id).select_related(
        'profile', 'preferences'
    ).filter(is_active=True, is_banned=False)

    results = []
    for candidate in candidates:
        if not hasattr(candidate, 'profile') or not hasattr(candidate, 'preferences'):
            continue
        score, breakdown = compute_compatibility(user, candidate)
        if score > 0:
            results.append({
                'user_id': candidate.pk,
                'score': score,
                'breakdown': breakdown,
            })
            # Persist to DB (upsert)
            a, b = (user, candidate) if user.pk < candidate.pk else (candidate, user)
            Match.objects.update_or_create(
                user_a=a, user_b=b, listing=None,
                defaults={'score': score, 'score_breakdown': breakdown}
            )

    results.sort(key=lambda x: x['score'], reverse=True)
    top20 = results[:20]
    cache.set(f'matches:{user_id}', top20, SUGGESTIONS_CACHE_TTL)
    return f"Computed {len(results)} matches for user {user_id}"


@shared_task
def recompute_all_matches():
    """Periodic task — recompute all match scores nightly."""
    user_ids = User.objects.filter(is_active=True, is_banned=False).values_list('pk', flat=True)
    for uid in user_ids:
        compute_matches_for_user.delay(uid)
    return f"Queued recompute for {len(user_ids)} users"
