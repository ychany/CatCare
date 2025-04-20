from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('board/', include('board.urls')),
    path('calendar/', include('calendar_app.urls')),
    path('care/', include('care_calendar.urls', namespace='care_calendar')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 