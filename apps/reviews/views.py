from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from core.permissions import IsOwner
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReportReviewSerializer

User = get_user_model()


class ReviewListCreateView(APIView):
    def get(self, request):
        reviews = Review.objects.filter(
            reviewer=request.user
        ).select_related('reviewer__profile', 'reviewee__profile')
        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request):
        serializer = ReviewCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs['pk'])
        return Review.objects.filter(
            reviewee=user
        ).select_related('reviewer__profile', 'reviewee__profile')


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewCreateSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        return get_object_or_404(Review, pk=self.kwargs['pk'], reviewer=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        return Response(ReviewSerializer(obj).data)


class ReportReviewView(APIView):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        serializer = ReportReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review.is_reported = True
        review.report_reason = serializer.validated_data['reason']
        review.save(update_fields=['is_reported', 'report_reason'])
        return Response({'message': 'Review reported. Our team will review it shortly.'})
