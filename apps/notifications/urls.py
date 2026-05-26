from django.urls import path
from .views import (
    NotificationListView,
    MarkReadView,
    MarkAllReadView,
    UnreadCountView,
    NotificationPreferenceView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("unread-count/", UnreadCountView.as_view(), name="notification-unread-count"),
    path("read-all/", MarkAllReadView.as_view(), name="notification-read-all"),
    path("preferences/", NotificationPreferenceView.as_view(), name="notification-preferences"),
    path("<int:pk>/read/", MarkReadView.as_view(), name="notification-read"),
]
