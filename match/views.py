from django.shortcuts import render

# Create your views here.
from django.views.generic import DetailView

from match.models import Match


class MatchDetailView(DetailView):
    model = Match
