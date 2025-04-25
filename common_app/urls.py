from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('edit/<int:pet_id>/', views.pet_edit, name='pet_edit'),
    path('update/<int:pet_id>/', views.pet_update, name='pet_update'),
    path('register/', views.pet_register, name='pet_register'),
] 