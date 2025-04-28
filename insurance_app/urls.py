from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    path('', views.main, name='main'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.insurance_detail, name='product_detail'),
    path('recommend/', views.select_pet_profile, name='select_pet_profile'),
    path('recommend/<int:pet_profile_id>/', views.insurance_recommend, name='recommend'),
    path('recommend/result/', views.recommend_result, name='recommend_result'),
    path('compare/', views.insurance_compare, name='compare'),
    path('inquiry/<int:product_id>/', views.inquiry, name='inquiry'),
    path('api/recommend/', views.api_recommend, name='api_recommend'),
    path('choose/<int:pet_profile_id>/<int:product_id>/', views.choose_insurance, name='choose'),
    path('recommend_form/<int:pet_profile_id>/', views.recommend_form, name='recommend_form'),
] 