from django.urls import path

from account.views import AccountDetailView, AccountListView, AccountMatchesAjaxView

urlpatterns = [
    path("list", AccountListView.as_view(), name="account-list"),
    path("<int:pk>", AccountDetailView.as_view(), name="account-detail"),
    path("<int:pk>/matches", AccountMatchesAjaxView.as_view(), name="account-matches"),
]
