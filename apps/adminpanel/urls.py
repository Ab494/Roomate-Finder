from django.urls import path
from .views import (
    PlatformStatsView, AdminUserListView, BanUserView, UnbanUserView,
    VerifyUserView, FlaggedListingsView, ApproveListingView, RejectListingView,
    BroadcastNotificationView,
)

urlpatterns = [
    path('stats/', PlatformStatsView.as_view(), name='admin-stats'),
    path('users/', AdminUserListView.as_view(), name='admin-users'),
    path('users/<int:pk>/ban/', BanUserView.as_view(), name='admin-ban-user'),
    path('users/<int:pk>/unban/', UnbanUserView.as_view(), name='admin-unban-user'),
    path('users/<int:pk>/verify/', VerifyUserView.as_view(), name='admin-verify-user'),
    path('listings/flagged/', FlaggedListingsView.as_view(), name='admin-flagged-listings'),
    path('listings/<int:pk>/approve/', ApproveListingView.as_view(), name='admin-approve-listing'),
    path('listings/<int:pk>/reject/', RejectListingView.as_view(), name='admin-reject-listing'),
    path('broadcast/', BroadcastNotificationView.as_view(), name='admin-broadcast'),
]
