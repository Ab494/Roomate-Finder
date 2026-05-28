from django.urls import path

from .views import ReportReviewView, ReviewDetailView, ReviewListCreateView, UserReviewsView

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="review-list"),
    path("user/<int:pk>/", UserReviewsView.as_view(), name="review-user"),
    path("<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
    path("<int:pk>/report/", ReportReviewView.as_view(), name="review-report"),
]
