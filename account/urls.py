from django.urls import path

from account.views import test_view, AccountDetailView

urlpatterns = [
    path("<int:pk>", AccountDetailView.as_view(), name="account-detail"),
    path("test", test_view, name="test_view"),
]
