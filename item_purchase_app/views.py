from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from .models import OtherPurchase
from common_app.models import Pet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .serializers import OtherPurchaseSerializer
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

# Create your views here.

@login_required
@require_http_methods(['GET'])
def other_purchase_management(request):
    # 기타 구매 관리 뷰
    # 월별 필터링
    month = request.GET.get('month')
    if month:
        year, mon = map(int, month.split('-'))
        start_date = datetime(year, mon, 1)
        end_date = datetime(year if mon<12 else year+1, mon%12+1, 1)
    else:
        today = datetime.now()
        start_date = datetime(today.year, today.month, 1)
        end_date = datetime(today.year if today.month<12 else today.year+1, today.month%12+1, 1)
    
    # 반려동물 필터링
    selected_pet_id = request.GET.get('pet')
    pets = Pet.objects.filter(owner=request.user)
    
    # 검색 필터링
    search = request.GET.get('search', '')
    qs = OtherPurchase.objects.filter(user=request.user, purchase_date__gte=start_date, purchase_date__lt=end_date)
    
    if selected_pet_id:
        qs = qs.filter(cat_id=selected_pet_id)
    if search:
        qs = qs.filter(product_name__icontains=search)
    
    # 총 합계
    total_price = qs.aggregate(total_price=Coalesce(Sum('price'), Value(0), output_field=DecimalField()))['total_price']
    
    context = {
        'purchases': qs.order_by('-purchase_date'),
        'current_month': start_date.strftime('%Y-%m'),
        'search': search,
        'total_price': total_price,
        'pets': pets,
        'selected_pet_id': selected_pet_id,
    }
    return render(request, 'item_purchase_app/other_purchase_management.html', context)

@login_required
@require_http_methods(['POST'])
def create_other_purchase(request):
    try:
        data = json.loads(request.body)
        default_cat = Pet.objects.filter(owner=request.user).first()
        purchase = OtherPurchase.objects.create(
            user=request.user,
            cat=default_cat,
            purchase_date=datetime.fromisoformat(data['purchase_date']),
            price=int(data.get('price', 0)),
            type=data.get('type', ''),
            product_name=data.get('product_name', ''),
            purchase_link=data.get('purchase_link', ''),
            rating=int(data.get('rating', 0)),
            memo=data.get('memo', ''),
        )
        return JsonResponse({'id': purchase.id}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class OtherPurchaseViewSet(ModelViewSet):
    queryset = OtherPurchase.objects.all().order_by('-purchase_date')
    serializer_class = OtherPurchaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset().filter(user=self.request.user)
        month = self.request.query_params.get('month')
        if month:
            y, m = map(int, month.split('-'))
            qs = qs.filter(purchase_date__year=y, purchase_date__month=m)
        pet = self.request.query_params.get('pet')
        if pet:
            qs = qs.filter(cat_id=pet)
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(product_name__icontains=search)
        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        total_price = queryset.aggregate(total_price=Coalesce(Sum('price'), Value(0), output_field=DecimalField()))['total_price']
        return JsonResponse({
            'purchases': serializer.data,
            'total_price': int(total_price) if total_price is not None else 0
        }, safe=False)

    def perform_create(self, serializer):
        pet_id = self.request.data.get('pet')
        if pet_id:
            pet = get_object_or_404(Pet, id=pet_id, owner=self.request.user)
        else:
            pet = Pet.objects.filter(owner=self.request.user).first()
        serializer.save(user=self.request.user, cat=pet)
