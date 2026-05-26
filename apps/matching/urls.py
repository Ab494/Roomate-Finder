from django.urls import path
from .views import MatchSuggestionsView, MatchRequestView, MatchActionView, MyMatchesView

urlpatterns = [
    path("suggestions/", MatchSuggestionsView.as_view(), name="match-suggestions"),
    path("request/", MatchRequestView.as_view(), name="match-request"),
    path("my/", MyMatchesView.as_view(), name="match-mine"),
    path("<int:pk>/accept/", MatchActionView.as_view(), {"action": "accept"}, name="match-accept"),
    path("<int:pk>/decline/", MatchActionView.as_view(), {"action": "decline"}, name="match-decline"),
]
