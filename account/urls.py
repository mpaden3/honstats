from django.urls import path

from account.views import AccountDetailView

urlpatterns = [
    path("<int:pk>", AccountDetailView.as_view(), name="account-detail"),
]
