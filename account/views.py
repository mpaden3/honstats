from django.http import HttpResponse
from django.views.generic import DetailView, ListView

from account.models import Account
from account.tasks import fetch_account_data, save_matches
from hon_api.tasks import match_history_overview
from match.constants import MODE_RANKED
from match.utils import determine_game_mode_table


class AccountDetailView(DetailView):
    model = Account

    def get_object(self, queryset=None):
        account = super().get_object()

        if account.should_be_updated():
            account = fetch_account_data(account.nickname)

            # get ranked match data
            match_data = match_history_overview(
                account, determine_game_mode_table(MODE_RANKED)
            )

            save_matches(match_data.values(), MODE_RANKED, account)

            account.update_current_mmr()
            account.save()
        return account


class AccountMatchesAjaxView(DetailView):
    model = Account
    template_name = "match/match_list_ajax.html"

    def get(self, request, *args, **kwargs):
        is_ajax = (
            request.META.get(
                "HTTP_X_REQUESTED_WITH",
            )
            == "XMLHttpRequest"
        )
        if not is_ajax:
            return HttpResponse(status=400)
        game_mode = self.request.GET["game_mode"].upper()
        self.object = self.get_object()
        if self.object.should_fetch_matches(game_mode):
            match_data = match_history_overview(
                self.object, determine_game_mode_table(game_mode)
            )
            save_matches(match_data.values(), game_mode, self.object)
            self.object.update_fetch_time(game_mode)

        context = self.get_context_data(object=self.object)
        context["matches"] = self.object.matches.filter(
            match__game_mode=game_mode
        ).order_by("-match__match_date")[:30]
        return self.render_to_response(context)


class AccountListView(ListView):
    model = Account
    queryset = (
        Account.objects.exclude(current_mmr__isnull=True)
        .filter(season_games_played__gt=100)
        .order_by("-current_mmr")
        .all()[:100]
    )


class AccountSearch(ListView):
    template_name = "account/account_search.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_term = ""
        self.exact_match = None

    def get(self, request, **kwargs):
        self.search_term = self.request.GET["s"]
        try:
            self.exact_match = Account.objects.get(nickname=self.search_term)
        except Account.DoesNotExist:
            pass
        return super().get(request, **kwargs)

    def get_queryset(self):
        return Account.objects.filter(nickname__icontains=self.search_term)[:100]

    def get_context_data(self, object_list=None, **kwargs):
        context_data = super().get_context_data(object_list=None, **kwargs)
        context_data["exact_match"] = self.exact_match

        return context_data
