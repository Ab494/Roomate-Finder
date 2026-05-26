from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        notif_type = self.request.query_params.get('type')
        unread_only = self.request.query_params.get('unread')
        if notif_type:
            qs = qs.filter(type=notif_type)
        if unread_only == 'true':
            qs = qs.filter(is_read=False)
        return qs


class MarkReadView(APIView):
    def put(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({'message': 'Marked as read'})


class MarkAllReadView(APIView):
    def put(self, request):
        count = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked_read': count})


class UnreadCountView(APIView):
    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer

    def get_object(self):
        pref, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return pref
