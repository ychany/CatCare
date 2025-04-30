from django.urls import path
from . import views

app_name = 'board_app'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('create/', views.post_create, name='create'),
    path('<int:post_id>/', views.post_detail, name='detail'),
    path('<int:post_id>/edit/', views.post_edit, name='edit'),
    path('<int:post_id>/delete/', views.post_delete, name='delete'),
    path('<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('<int:post_id>/comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
    path('<int:post_id>/like/', views.post_like, name='like'),
] 