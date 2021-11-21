"""honstats URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from blog.views import HomepageView

urlpatterns = [
    path("", HomepageView.as_view(), name="homepage"),
    path(
        "about/",
        TemplateView.as_view(template_name="../templates/about.html"),
        name="about",
    ),
    path(
        "qna/",
        TemplateView.as_view(template_name="../templates/qna.html"),
        name="qna",
    ),
    path("admin/", admin.site.urls),
    path("match/", include("match.urls")),
    path("account/", include("account.urls")),
    path("blog/", include("blog.urls")),
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="../templates/robots.txt", content_type="text/plain"
        ),
    ),
]
