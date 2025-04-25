from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import InsuranceProduct, InsuranceCompany

def insurance_main(request):
    return render(request, 'insurance/main.html')

def product_list(request):
    products = InsuranceProduct.objects.all().select_related('company')
    return render(request, 'insurance/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(InsuranceProduct, pk=pk)
    return render(request, 'insurance/product_detail.html', {'product': product})

@login_required
def insurance_recommend(request):
    if request.method == 'POST':
        # 추천 로직 구현 예정
        return render(request, 'insurance/recommend_result.html')
    return render(request, 'insurance/recommend.html')

@login_required
def insurance_compare(request):
    products = InsuranceProduct.objects.all().select_related('company')
    return render(request, 'insurance/compare.html', {'products': products})
