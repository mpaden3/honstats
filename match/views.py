from django.views.generic import DetailView, ListView

from match.models import Match
from match.tasks import fetch_match_data


class MatchDetailView(DetailView):
    model = Match

    def get_object(self, queryset=None):
        obj: Match = super(MatchDetailView, self).get_object(queryset=queryset)
        if obj.parsed_level == Match.KNOWN:
            obj = fetch_match_data(obj.match_id)

        return obj

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        context["players"] = self.object.player_set.all().order_by("position")

        return context


class MatchListView(ListView):
    model = Match
    paginate_by = 50
