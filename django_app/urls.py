"""
URL configuration for django_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.views.generic.base import RedirectView

from . import views
from .views import CustomLoginView
from .views import CustomRegisterView
from .views import logout_view

from django.urls import re_path

urlpatterns = [
    path('', views.table_main, name='table_main'),
    path('admin/', admin.site.urls),
    path('check_process_status/', views.check_process_status, name='check_process_status'),
    path('load/', views.load, name='load'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout_view'),
    path('registration/', CustomRegisterView.as_view(), name='registration'),
    path('save/', views.save, name='save'),
    re_path(r'favicon\.ico$', RedirectView.as_view(url='/favicon.ico', permanent=True)),
]