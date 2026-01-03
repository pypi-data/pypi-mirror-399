"""
URL configuration for _project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

from django.http import HttpRequest, HttpResponse
from django.urls import path, include

from rest_framework_statelessauth.config import StatelessAuthConfig
from rest_framework_statelessauth.contrib.auth.models import User

sl_config = StatelessAuthConfig.instance().get_engine("default")
def home_page (request: HttpRequest):
    user: "User | None" = request.user

    username = "Anonymous"
    if user is not None:
        username = user.username

    return HttpResponse(f"Hello, {username} !")

urlpatterns = [
    path('account/', include(sl_config.urlpatterns)),
    path('', home_page)
]


urlpatterns.append(path('prometheus/', include('django_prometheus.urls')))
#urlpatterns.append(path('', include('myapp.urls')))
