"""
URL configuration for animal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from common_app import views
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('login', permanent=False), name='root_redirect'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page=settings.LOGIN_URL
    ), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('home/', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('pets/', include('common_app.urls')),
    path('board/', include('board_app.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('care/', include('care_calendar.urls', namespace='care_calendar')),
    path('food/', include('food_calendar.urls')),
    path('items/', include('item_purchase_app.urls', namespace='item_purchase_app')),
    path('weight-tracker/', include('weight_tracker_app.urls')),
    path('insurance/', include('insurance_app.urls')),
    path('community/', include('community_app.urls', namespace='community_app')),
    path('emergency/', include('emergency_app.urls', namespace='emergency_app')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
