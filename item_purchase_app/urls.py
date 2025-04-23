from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'item_purchase_app'

urlpatterns = [
    # 관리 페이지
    path('', views.other_purchase_management, name='management'),
    # 생성 엔드포인트
    path('create/', views.create_other_purchase, name='create'),
]

# DRF API 라우터 설정
router = DefaultRouter()
# ViewSet 등록 (베이스네임: otherpurchase)
router.register(r'otherpurchase', views.OtherPurchaseViewSet, basename='otherpurchase')

urlpatterns += [
    path('api/', include(router.urls)),
] 