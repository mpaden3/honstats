from django.urls import path

from account.views import AccountDetailView, AccountListView

urlpatterns = [
    path("list", AccountListView.as_view(), name="account-list"),
    path("<int:pk>", AccountDetailView.as_view(), name="account-detail"),
]
