from django.utils import timezone
from django.views.generic import DetailView, ListView

from account.models import Account
from account.tasks import fetch_player_data


class AccountDetailView(DetailView):
    model = Account

    def get_object(self, queryset=None):
        account = super(AccountDetailView, self).get_object()

        if (
            account.fetched_date is None
            or account.fetched_date + timezone.timedelta(seconds=300) < timezone.now()
        ):
            account = fetch_player_data(account.nickname)
        return account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matches"] = self.object.matches.all().order_by("-match__match_date")[
            :30
        ]

        return context


class AccountListView(ListView):
    model = Account
    queryset = (
        Account.objects.exclude(current_mmr__isnull=True)
        .filter(season_games_played__gt=100)
        .order_by("-current_mmr")
        .all()[:100]
    )
