from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg

from core.permissions import IsAdminUser
from apps.profiles.serializers import UserSerializer
from apps.listings.models import Listing
from apps.listings.serializers import ListingSerializer
from apps.matching.models import Match
from apps.notifications.models import Notification
from apps.notifications.tasks import send_bulk_notification

User = get_user_model()


class PlatformStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            'users': {
                'total': User.objects.count(),
                'verified': User.objects.filter(is_verified=True).count(),
                'banned': User.objects.filter(is_banned=True).count(),
                'seekers': User.objects.filter(role='seeker').count(),
                'listers': User.objects.filter(role='lister').count(),
            },
            'listings': {
                'total': Listing.objects.count(),
                'active': Listing.objects.filter(status='active').count(),
                'flagged': Listing.objects.filter(is_flagged=True).count(),
                'pending_approval': Listing.objects.filter(is_approved=False).count(),
            },
            'matches': {
                'total': Match.objects.count(),
                'accepted': Match.objects.filter(status='accepted').count(),
                'pending': Match.objects.filter(status='pending').count(),
                'avg_score': round(Match.objects.aggregate(Avg('score'))['score__avg'] or 0, 1),
            },
            'notifications': {
                'unread': Notification.objects.filter(is_read=False).count(),
            },
        })


class AdminUserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        role = self.request.query_params.get('role')
        is_banned = self.request.query_params.get('is_banned')
        search = self.request.query_params.get('search')
        if role:
            qs = qs.filter(role=role)
        if is_banned is not None:
            qs = qs.filter(is_banned=is_banned == 'true')
        if search:
            qs = qs.filter(email__icontains=search)
        return qs


class BanUserView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_staff:
            return Response({'error': 'Cannot ban staff users'}, status=status.HTTP_403_FORBIDDEN)
        user.is_banned = True
        user.is_active = False
        user.save(update_fields=['is_banned', 'is_active'])
        return Response({'message': f'{user.email} has been banned'})


class UnbanUserView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_banned = False
        user.is_active = True
        user.save(update_fields=['is_banned', 'is_active'])
        return Response({'message': f'{user.email} has been unbanned'})


class VerifyUserView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        return Response({'message': f'{user.email} is now verified'})


class FlaggedListingsView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ListingSerializer

    def get_queryset(self):
        return Listing.objects.filter(
            is_flagged=True
        ).select_related('owner__profile').prefetch_related('photos')


class ApproveListingView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        listing.is_approved = True
        listing.is_flagged = False
        listing.save(update_fields=['is_approved', 'is_flagged'])
        return Response({'message': f'Listing "{listing.title}" approved'})


class RejectListingView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        listing.is_approved = False
        listing.status = 'paused'
        listing.save(update_fields=['is_approved', 'status'])
        # Notify owner
        send_bulk_notification.delay(
            user_ids=[listing.owner_id],
            message=f'Your listing "{listing.title}" has been removed for violating our guidelines.',
            notif_type='listing',
            channel='both',
        )
        return Response({'message': f'Listing "{listing.title}" rejected'})


class BroadcastNotificationView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        message = request.data.get('message', '').strip()
        channel = request.data.get('channel', 'in_app')
        if not message:
            return Response({'error': 'message is required'}, status=400)
        user_ids = list(User.objects.filter(is_active=True).values_list('pk', flat=True))
        send_bulk_notification.delay(user_ids, message, notif_type='system', channel=channel)
        return Response({'message': f'Broadcast queued for {len(user_ids)} users'})
