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
from .utils import recommend_insurance, calculate_sure_index, calculate_age, get_pred, make_sure_score, get_coverage_vector, jaccard_similarity, get_flat_coverage_vector, flatten_coverage_keys
from .knn_utils import predict_insurance, update_user_choice
import json
from pathlib import Path
from django.db import models

@login_required
def main(request):
    user_pets = Pet.objects.filter(owner=request.user)
    context = {
        'user_pets': user_pets
    }
    return render(request, 'insurance/main.html', context)

@login_required
def select_pet_profile(request):
    user_pets = Pet.objects.filter(owner=request.user)
    
    if not user_pets.exists():
        messages.info(request, '보험 추천을 받으시려면 먼저 반려동물을 등록해주세요.')
        return redirect('pets:pet_register')
    
    if user_pets.count() == 1:
        return redirect('insurance:recommend', pet_profile_id=user_pets.first().id)
    
    context = {
        'user_pets': user_pets
    }
    return render(request, 'insurance/select_pet_profile.html', context)

def product_list(request):
    products = InsuranceProduct.objects.all().select_related('company')
    return render(request, 'insurance/product_list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(InsuranceProduct, pk=pk)
    return render(request, 'insurance/product_detail.html', {'product': product})

@login_required
def insurance_recommend(request, pet_profile_id):
    pet = get_object_or_404(Pet, id=pet_profile_id, owner=request.user)

    # 모든 보험 상품 가져오기
    products = InsuranceProduct.objects.all()

    # 전체 보장항목 키(flat) 추출
    all_coverage_keys = set()
    for product in products:
        all_coverage_keys.update(flatten_coverage_keys(product.coverage_details))
    all_coverage_keys = sorted(list(all_coverage_keys), key=lambda x: str(x))

    # 유저의 보장 선호 벡터 (예시: 모든 항목을 선호한다고 가정)
    user_vector = [1 for _ in all_coverage_keys]
    # 실제로는 유저의 선호를 받아서 벡터 생성 가능

    # 각 상품의 보장항목 벡터 및 matching_score(자카드 유사도) 계산
    before_ranking = []
    for product in products:
        product_vector = get_flat_coverage_vector(product.coverage_details, all_coverage_keys)
        matching_score = jaccard_similarity(user_vector, product_vector)
        temp_detail = {}
        temp_detail['product'] = product
        temp_detail['company_score'] = float(product.company.rating) if product.company and product.company.rating else 0.0
        # price_score: InsuranceDetail이 있으면 평균값, 없으면 base_price 사용
        details = getattr(product, 'insurancedetail_set', None)
        if details and details.exists():
            price_score = float(details.aggregate(models.Avg('price_score'))['price_score__avg'] or 0)
        else:
            price_score = float(product.base_price)
        temp_detail['price_score'] = price_score
        temp_detail['matching_score'] = matching_score
        # 보장 항목 수
        temp_detail['cover_count'] = len(flatten_coverage_keys(product.coverage_details))
        # sure_score
        temp_detail['sure_score'] = make_sure_score(temp_detail['company_score'], price_score, matching_score)
        # 보장항목 이름 변환
        cover_path = Path(__file__).parent / 'fixtures' / 'cover.json'
        disease_path = Path(__file__).parent / 'fixtures' / 'disease.json'
        cover_map = {}
        disease_map = {}
        if cover_path.exists():
            with open(cover_path, encoding='utf-8') as f:
                for item in json.load(f):
                    cover_map[item['pk']] = item['fields']['detail']
        if disease_path.exists():
            with open(disease_path, encoding='utf-8') as f:
                for item in json.load(f):
                    disease_map[item['pk']] = item['fields']['name']
        product.coverage_details_verbose = {}
        for key, value in product.coverage_details.items():
            if isinstance(value, list):
                product.coverage_details_verbose[key] = [cover_map.get(i) or disease_map.get(i) or str(i) for i in value]
            else:
                product.coverage_details_verbose[key] = value
        # 특별혜택 이름 변환
        if hasattr(product, 'special_benefits') and isinstance(product.special_benefits, list):
            product.special_benefits = [cover_map.get(i, str(i)) for i in product.special_benefits]
        before_ranking.append(temp_detail)

    # 다양한 기준으로 정렬
    sure_ranking = sorted(before_ranking, key=lambda item: -item['sure_score'])
    price_ranking = sorted(before_ranking, key=lambda item: item['price_score'])
    cover_ranking = sorted(before_ranking, key=lambda item: -item['cover_count'])

    context = {
        'pet': pet,
        'sure_ranking': sure_ranking,
        'price_ranking': price_ranking,
        'cover_ranking': cover_ranking,
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
    # pet_id 쿼리파라미터로 받기
    pet_id = request.GET.get('pet_id')
    pet = None
    pet_type = 'dog'
    age = 3
    weight = None
    if pet_id:
        try:
            pet = Pet.objects.get(id=pet_id, owner=request.user)
            pet_type = pet.pet_type if hasattr(pet, 'pet_type') else (pet.species if hasattr(pet, 'species') else 'dog')
            if hasattr(pet, 'birth_date') and pet.birth_date:
                from .utils import calculate_age
                age = calculate_age(pet.birth_date)
            if hasattr(pet, 'weight') and pet.weight:
                weight = pet.weight
        except Pet.DoesNotExist:
            pass

    # 모든 보험 상품 가져오기
    products = InsuranceProduct.objects.all()

    # cover_map, disease_map 생성 (추천/상세와 동일)
    cover_path = Path(__file__).parent / 'fixtures' / 'cover.json'
    disease_path = Path(__file__).parent / 'fixtures' / 'disease.json'
    cover_map = {}
    disease_map = {}
    if cover_path.exists():
        with open(cover_path, encoding='utf-8') as f:
            for item in json.load(f):
                cover_map[item['pk']] = item['fields']['detail']
    if disease_path.exists():
        with open(disease_path, encoding='utf-8') as f:
            for item in json.load(f):
                disease_map[item['pk']] = item['fields']['name']

    # 보장 내용 키 추출 및 각 상품의 보장/특별보장 이름 변환 + SURE 점수 계산 (추천과 동일하게)
    # 전체 보장항목 키(flat) 추출 (추천과 동일)
    all_coverage_keys = set()
    for product in products:
        all_coverage_keys.update(flatten_coverage_keys(product.coverage_details))
    all_coverage_keys = sorted(list(all_coverage_keys), key=lambda x: str(x))

    processed = []
    for product in products:
        # 보장 항목 이름 리스트로 변환
        product.coverage_details_verbose = {}
        for key, value in product.coverage_details.items():
            if isinstance(value, list):
                product.coverage_details_verbose[key] = [cover_map.get(i) or disease_map.get(i) or str(i) for i in value]
            else:
                product.coverage_details_verbose[key] = value
        # 특별보장(특별혜택) 이름 리스트로 변환
        if not isinstance(product.special_benefits, list):
            product.special_benefits = []
        else:
            product.special_benefits = [cover_map.get(i) or disease_map.get(i) or str(i) for i in product.special_benefits]
        # SURE 점수 계산 (추천과 동일)
        company_score = float(product.company.rating) if product.company and product.company.rating else 0.0
        details = getattr(product, 'insurancedetail_set', None)
        if details and details.exists():
            price_score = float(details.aggregate(models.Avg('price_score'))['price_score__avg'] or 0)
        else:
            price_score = float(product.base_price)
        user_vector = [1 for _ in all_coverage_keys]
        product_vector = get_flat_coverage_vector(product.coverage_details, all_coverage_keys)
        matching_score = jaccard_similarity(user_vector, product_vector)
        sure_score = make_sure_score(company_score, price_score, matching_score)
        processed.append((product, sure_score))

    context = {
        'products': processed,
        'coverage_keys': sorted(all_coverage_keys, key=lambda x: str(x)),
        'pet': pet,
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

    # cover_map, disease_map 생성 (recommend와 동일)
    cover_path = Path(__file__).parent / 'fixtures' / 'cover.json'
    disease_path = Path(__file__).parent / 'fixtures' / 'disease.json'
    cover_map = {}
    disease_map = {}
    if cover_path.exists():
        with open(cover_path, encoding='utf-8') as f:
            for item in json.load(f):
                cover_map[item['pk']] = item['fields']['detail']
    if disease_path.exists():
        with open(disease_path, encoding='utf-8') as f:
            for item in json.load(f):
                disease_map[item['pk']] = item['fields']['name']

    # 보장 id를 이름/설명으로 변환하여 context에 전달
    coverage_details_verbose = {}
    for key, value in product.coverage_details.items():
        if isinstance(value, list):
            coverage_details_verbose[key] = [cover_map.get(i) or disease_map.get(i) or str(i) for i in value]
        else:
            coverage_details_verbose[key] = value
    if not isinstance(product.special_benefits, list):
        special_benefits_verbose = []
    else:
        special_benefits_verbose = [cover_map.get(i) or disease_map.get(i) or str(i) for i in product.special_benefits]

    context = {
        'product': product,
        'coverage_details_verbose': coverage_details_verbose,
        'special_benefits_verbose': special_benefits_verbose
    }
    return render(request, 'insurance/product_detail.html', context)

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
