from django import forms

from account.models import Account
from account.tasks import fetch_player_data


class SearchForm(forms.Form):
    search_term = forms.CharField(
        label="Search nickname or match id", max_length=100, required=True
    )

    def fetch_data(self):
        nickname = self.cleaned_data["search_term"]
        # TODO last_fetch_date, SQL injection, match search
        # TODO actual database search
        if Account.objects.filter(nickname__iexact=nickname).exists():
            account = Account.objects.get(nickname__iexact=nickname)
            return account.account_id

        return fetch_player_data(nickname)
