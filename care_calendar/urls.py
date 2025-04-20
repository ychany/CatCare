from django.urls import path
from . import views

app_name = 'care_calendar'

urlpatterns = [
    path('', views.care_calendar, name='care_calendar'),
    path('events/', views.get_events, name='get_events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:event_id>/update/', views.update_event, name='update_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('previous-care/<int:pet_id>/<str:category>/', views.get_previous_care, name='get_previous_care'),
] 