from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    path('', views.insurance_main, name='main'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('recommend/', views.insurance_recommend, name='recommend'),
    path('compare/', views.insurance_compare, name='compare'),
] 