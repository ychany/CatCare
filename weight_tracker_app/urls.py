from django.urls import path
from . import views

urlpatterns = [
    path('', views.weight_tracker_view, name='weight_tracker'),
    path('api/weights/', views.weight_list, name='weight_list'),
] 