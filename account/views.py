from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView
from django.utils import timezone

from account.forms import SearchForm
from account.models import Account
from account.tasks import fetch_player_data
from match.models import Match


class HomepageView(FormView):
    template_name = "homepage.html"
    form_class = SearchForm
    success_url = None

    def form_valid(self, form):

        # handle match
        if form.is_match_id():
            self.success_url = reverse("match-detail", args=[form.get_search_term()])
            return super().form_valid(form)

        if Account.objects.filter(nickname__iexact=form.get_search_term()).exists():
            account = Account.objects.get(nickname__iexact=form.get_search_term())
        else:
            account = fetch_player_data(form.get_search_term())
        self.success_url = reverse("account-detail", args=[account.account_id])

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matches"] = Match.objects.exclude(parsed_level=Match.KNOWN).order_by("-match_date")[:30]
        return context


class AccountDetailView(DetailView):
    model = Account

    def get_object(self, queryset=None):
        account = super(AccountDetailView, self).get_object()

        if (
                account.fetched_date is None
                or account.fetched_date + timezone.timedelta(seconds=900) < timezone.now()
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
    paginate_by = 50
