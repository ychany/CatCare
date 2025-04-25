from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import InsuranceProduct, InsuranceCompany, InsuranceInquiry, PetProfile, InsuranceChoice
from common_app.models import Pet
from .utils import recommend_insurance, calculate_sure_index
from .knn_utils import predict_insurance, update_user_choice

@login_required
def insurance_main(request):
    return render(request, 'insurance/main.html')

@login_required
def select_pet_profile(request):
    pets = Pet.objects.filter(owner=request.user)
    if not pets.exists():
        messages.info(request, '반려동물을 먼저 등록해주세요.')
        return redirect('pets:pet_register')
    elif pets.count() == 1:
        return redirect('insurance:recommend', pet_profile_id=pets.first().id)
    
    return render(request, 'insurance/select_pet_profile.html', {'pets': pets})

def product_list(request):
    products = InsuranceProduct.objects.all().select_related('company')
    return render(request, 'insurance/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(InsuranceProduct, pk=pk)
    return render(request, 'insurance/product_detail.html', {'product': product})

@login_required
def insurance_recommend(request, pet_profile_id):
    pet = get_object_or_404(Pet, id=pet_profile_id, owner=request.user)
    
    # KNN을 사용하여 보험 추천
    recommended_products = predict_insurance(pet)
    
    # 추천된 보험 상품이 없는 경우 기본 추천 로직 사용
    if not recommended_products:
        recommended_products = InsuranceProduct.objects.filter(
            min_age__lte=pet.get_age(),
            max_age__gte=pet.get_age()
        ).order_by('-sure_index')[:5]
    
    context = {
        'pet': pet,
        'recommended_products': recommended_products,
    }
    return render(request, 'insurance/recommend.html', context)

def recommend_result(request):
    if request.method == 'POST':
        pet_name = request.POST.get('pet_name')
        pet_type = request.POST.get('pet_type')
        pet_birth = datetime.strptime(request.POST.get('pet_birth'), '%Y-%m-%d').date()
        
        recommended_products = recommend_insurance(pet_type, pet_birth)
        return render(request, 'insurance/recommend_result.html', {
            'products': recommended_products,
            'pet_name': pet_name
        })
    return redirect('insurance:recommend')

@login_required
def insurance_compare(request):
    # 모든 보험 상품 가져오기
    products = InsuranceProduct.objects.all()
    
    # 보장 내용 키 추출
    coverage_keys = set()
    for product in products:
        coverage_keys.update(product.coverage_details.keys())
    
    context = {
        'products': products,
        'coverage_keys': sorted(coverage_keys)
    }
    return render(request, 'insurance/compare.html', context)

@csrf_exempt
@require_POST
def api_recommend(request):
    try:
        pet_type = request.POST.get('pet_type')
        pet_birth = datetime.strptime(request.POST.get('pet_birth'), '%Y-%m-%d').date()
        
        recommended_products = recommend_insurance(pet_type, pet_birth)
        
        result = []
        for product in recommended_products:
            result.append({
                'id': product.id,
                'name': product.name,
                'company': product.company.name,
                'base_price': float(product.base_price),
                'coverage_details': product.coverage_details
            })
        
        return JsonResponse({'status': 'success', 'products': result})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def inquiry(request, product_id):
    product = get_object_or_404(InsuranceProduct, id=product_id)
    
    if request.method == 'POST':
        try:
            inquiry = InsuranceInquiry.objects.create(
                product=product,
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                pet_name=request.POST.get('pet_name'),
                pet_type=request.POST.get('pet_type'),
                pet_age=request.POST.get('pet_age'),
                inquiry_type=request.POST.get('inquiry_type'),
                content=request.POST.get('content')
            )
            
            # 이메일 알림 발송
            send_mail(
                f'[펫보험] {product.name} 문의가 접수되었습니다.',
                f'''
안녕하세요, {inquiry.name}님.

{product.name} 보험 상품에 대한 문의가 정상적으로 접수되었습니다.
문의 내용: {inquiry.content}

빠른 시일 내에 답변 드리도록 하겠습니다.

감사합니다.
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [inquiry.email],
                fail_silently=False,
            )
            
            messages.success(request, '문의가 성공적으로 접수되었습니다. 이메일로 확인해주세요.')
            return redirect('insurance:product_detail', product_id=product.id)
            
        except Exception as e:
            messages.error(request, f'문의 접수 중 오류가 발생했습니다: {str(e)}')
    
    return render(request, 'insurance/inquiry.html', {'product': product})

@login_required
def insurance_detail(request, product_id):
    product = get_object_or_404(InsuranceProduct, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'insurance/detail.html', context)

@login_required
def choose_insurance(request, pet_profile_id, product_id):
    pet_profile = get_object_or_404(PetProfile, id=pet_profile_id, user=request.user)
    product = get_object_or_404(InsuranceProduct, id=product_id)
    
    # 사용자의 보험 선택 기록 업데이트
    update_user_choice(pet_profile, product)
    
    return JsonResponse({
        'status': 'success',
        'message': '보험이 성공적으로 선택되었습니다.'
    })
