from account.models import Account
from account.tasks import fetch_player_data
from django.http import HttpResponse
from django.views.generic import DetailView


def test_view(request):
    fetch_player_data("yeo")
    return HttpResponse("Success")


class AccountDetailView(DetailView):
    model = Account
