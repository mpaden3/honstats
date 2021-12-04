from django.views.generic import DetailView, ListView

from log_parser.tasks import parse_match_data
from match.exceptions import ReplayNotFoundException
from match.models import Match
from match.tasks import fetch_match_data


class MatchDetailView(DetailView):
    model = Match

    def get_object(self, queryset=None):
        match_id = self.kwargs.get(self.pk_url_kwarg)
        try:
            obj: Match = Match.objects.get(match_id=match_id)
        except Match.DoesNotExist:
            obj = fetch_match_data(match_id)

        if obj.parsed_level == Match.KNOWN:
            obj = fetch_match_data(match_id)

        if not obj.is_parsed() and obj.should_be_parsed():
            obj.add_attempt()
            try:
                obj = parse_match_data(obj.match_id)
            except ReplayNotFoundException:
                obj.parsed_level = Match.NOT_FOUND
                obj.save()

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["players"] = self.object.player_set.order_by("position")

        return context


class MatchListView(ListView):
    model = Match
    paginate_by = 50
    queryset = Match.objects.exclude(parsed_level=Match.KNOWN)
