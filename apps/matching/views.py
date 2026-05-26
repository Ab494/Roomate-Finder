# This file contains API views for the roommate matching system.
# Handles match suggestions, requests, accept/decline actions, and match listing.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from .models import Match
from .serializers import MatchSerializer, MatchSuggestionSerializer, MatchRequestSerializer
from .tasks import compute_matches_for_user
from .algorithm import compute_compatibility
from apps.notifications.tasks import send_notification

# Get the custom User model
User = get_user_model()


class MatchSuggestionsView(APIView):
    """API view to get personalized roommate suggestions for the current user."""

    def get(self, request):
        user = request.user
        # Check cache first for performance (30-minute TTL)
        cached = cache.get(f"matches:{user.pk}")

        if not cached:
            # Generate suggestions if not cached
            # Get all active, non-banned users except current user
            candidates = (
                User.objects.exclude(pk=user.pk)
                .select_related("profile", "preferences")  # Optimize database queries
                .filter(is_active=True, is_banned=False)
            )

            results = []
            for candidate in candidates:
                # Skip users without complete profiles/preferences
                if not hasattr(candidate, "profile") or not hasattr(candidate, "preferences"):
                    continue

                # Calculate compatibility score using matching algorithm
                score, breakdown = compute_compatibility(user, candidate)

                # Only include matches with positive compatibility
                if score > 0:
                    results.append(
                        {"user_id": candidate.pk, "score": score, "breakdown": breakdown}  # Detailed scoring breakdown
                    )

            # Sort by compatibility score (highest first)
            results.sort(key=lambda x: x["score"], reverse=True)
            # Limit to top 20 matches for performance
            cached = results[:20]
            # Cache results for 30 minutes
            cache.set(f"matches:{user.pk}", cached, 60 * 30)

            # Trigger asynchronous recomputation for future requests
            compute_matches_for_user.delay(user.pk)

        # Serialize and return suggestions
        serializer = MatchSuggestionSerializer(cached, many=True)
        return Response({"count": len(cached), "results": serializer.data})


class MatchRequestView(APIView):
    """API view to create a new match request with another user."""

    def post(self, request):
        # Validate input data using serializer
        serializer = MatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get target user and validate they exist and are active
        target = get_object_or_404(
            User, pk=serializer.validated_data["target_user_id"], is_active=True, is_banned=False
        )

        # Handle optional listing-specific match
        listing_id = serializer.validated_data.get("listing_id")
        listing = None
        if listing_id:
            from apps.listings.models import Listing

            listing = get_object_or_404(Listing, pk=listing_id)

        # Ensure consistent ordering (user_a always has smaller pk)
        user_a, user_b = (request.user, target) if request.user.pk < target.pk else (target, request.user)

        # Calculate compatibility score
        score, breakdown = compute_compatibility(request.user, target)

        # Create or get existing match
        match, created = Match.objects.get_or_create(
            user_a=user_a,
            user_b=user_b,
            listing=listing,
            defaults={"score": score, "score_breakdown": breakdown, "status": "pending"},  # Start as pending
        )

        if not created:
            # Match already exists
            return Response({"message": "Match request already exists", "match": MatchSerializer(match).data})

        # Send notification to target user
        send_notification.delay(
            user_id=target.pk,
            message=f"{request.user.profile.full_name} wants to be your roommate!",
            notif_type="match_request",
            channel="in_app",
        )

        return Response(MatchSerializer(match).data, status=status.HTTP_201_CREATED)


class MatchActionView(APIView):
    """API view to accept or decline match requests."""

    def put(self, request, pk, action):
        # Get the match and validate user has permission
        match = get_object_or_404(Match, pk=pk)
        user = request.user

        # Ensure user is part of this match
        if user not in (match.user_a, match.user_b):
            return Response({"error": "Not your match"}, status=status.HTTP_403_FORBIDDEN)

        if action == "accept":
            # Accept the match
            match.status = "accepted"
            # Notify the other user
            other_user = match.user_b if user == match.user_a else match.user_a
            send_notification.delay(
                user_id=other_user.pk,
                message=f"{user.profile.full_name} accepted your roommate request!",
                notif_type="match_accepted",
                channel="both",  # Send via both in-app and SMS/email
            )
        elif action == "decline":
            # Decline the match
            match.status = "declined"
        else:
            return Response({"error": "Invalid action"}, status=400)

        match.save()
        return Response(MatchSerializer(match).data)


class MyMatchesView(generics.ListAPIView):
    """API view to list all matches for the current user."""

    serializer_class = MatchSerializer

    def get_queryset(self):
        user = self.request.user

        # Get optional status filter from query parameters
        status_filter = self.request.query_params.get("status")

        # Get all matches where user is involved
        qs = Match.objects.filter(user_a=user).union(Match.objects.filter(user_b=user)).order_by("-score")

        # Apply status filter if provided
        if status_filter:
            qs = Match.objects.filter(status=status_filter).filter(user_a=user) | Match.objects.filter(
                status=status_filter
            ).filter(user_b=user)

        return qs
