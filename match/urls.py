from django.urls import path

from match.views import MatchDetailView, MatchListView

urlpatterns = [
    path("list", MatchListView.as_view(), name="match-list"),
    path("<int:pk>", MatchDetailView.as_view(), name="match-detail"),
]
