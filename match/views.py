from django.http import Http404
from django.views.generic import DetailView, ListView

from log_parser.tasks import parse_match_data
from match.exceptions import ReplayNotFoundException
from match.models import Match
from match.tasks import fetch_match_data


class MatchDetailView(DetailView):
    model = Match

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            self.object = fetch_match_data(self.kwargs["pk"])
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        obj: Match = super(MatchDetailView, self).get_object(queryset=queryset)
        if obj.parsed_level == Match.KNOWN:
            obj = fetch_match_data(obj.match_id)

        if not obj.is_parsed():
            try:
                obj = parse_match_data(obj.match_id)
            except ReplayNotFoundException:
                obj.parsed_level = Match.NOT_FOUND
                obj.save()

        return obj

    def get_context_data(self, **kwargs):
        context = super(MatchDetailView, self).get_context_data(**kwargs)
        context["players"] = self.object.player_set.all().order_by("position")

        return context


class MatchListView(ListView):
    model = Match
    paginate_by = 50
    queryset = Match.objects.exclude(parsed_level=Match.KNOWN)
