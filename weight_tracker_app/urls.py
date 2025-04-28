from django.urls import path
from . import views

urlpatterns = [
    path('', views.weight_tracker_view, name='weight_tracker'),
    path('api/weights/', views.weight_list, name='weight_list'),
    path('api/weights/<int:pk>/', views.weight_delete, name='weight_delete'),
] 