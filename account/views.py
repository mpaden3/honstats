from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView
from django.utils import timezone

from account.forms import SearchForm
from account.models import Account
from account.tasks import fetch_player_data


class HomepageView(FormView):
    template_name = "homepage.html"
    form_class = SearchForm
    success_url = None

    def form_valid(self, form):
        account = form.fetch_data()
        if account:
            self.success_url = reverse("account-detail", args=[account.account_id])
        return super().form_valid(form)


class AccountDetailView(DetailView):
    model = Account

    def get_object(self, queryset=None):
        object = super(AccountDetailView, self).get_object()

        if object.fetched_date is None or object.fetched_date + timezone.timedelta(seconds=900) < timezone.now():
            object = fetch_player_data(object.nickname)
        return object



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matches"] = self.object.matches.all().order_by("-match__match_date")

        return context


class AccountListView(ListView):
    model = Account
    paginate_by = 50
