from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('<int:pet_id>/edit/', views.pet_edit, name='edit'),
    path('<int:pet_id>/update/', views.pet_update, name='update'),
] 