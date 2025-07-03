from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # 루트 URL을 로그인 페이지로 직접 리다이렉트
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='root_redirect'),
    # 기존 홈페이지 URL
    path('home/', include('core.urls')),
    path('board/', include('board.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('care/', include('care_calendar.urls', namespace='care_calendar')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='common_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/accounts/login/'), name='logout'),
    path('', include('common_app.urls')),
    path('weight/', include('weight_tracker_app.urls')),
    path('insurance/', include('insurance_app.urls', namespace='insurance')),
    path('items/', include('item_purchase_app.urls')),
    path('food/', include('food_calendar.urls')),
    path('community/', include('community_app.urls', namespace='community_app')),
    path('emergency/', include('emergency_app.urls', namespace='emergency_app')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 