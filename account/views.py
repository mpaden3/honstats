from django.urls import reverse
from django.views.generic import DetailView, FormView

from account.forms import SearchForm
from account.models import Account


class HomepageView(FormView):
    template_name = "homepage.html"
    form_class = SearchForm
    success_url = None

    def form_valid(self, form):
        account_id = form.fetch_data()
        if account_id:
            self.success_url = reverse("account-detail", args=[account_id])
        return super().form_valid(form)


class AccountDetailView(DetailView):
    model = Account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["matches"] = self.object.matches.all().order_by("-match__match_date")

        return context
