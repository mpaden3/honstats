from django import forms

from account.models import Account
from account.tasks import fetch_player_data


class SearchForm(forms.Form):
    search_term = forms.CharField(
        label="Search nickname or Match ID", max_length=100, required=True
    )

    def fetch_data(self):
        nickname = self.cleaned_data["search_term"]
        # TODO SQL injection, match search
        # TODO actual database search
        if Account.objects.filter(nickname__iexact=nickname).exists():
            account = Account.objects.get(nickname__iexact=nickname)
            return account

        return fetch_player_data(nickname)

    def is_match_id(self):
        search_term = self.cleaned_data["search_term"]
        return search_term.isnumeric()

    def get_search_term(self):
        return self.cleaned_data["search_term"]
