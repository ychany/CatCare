from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
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
from numpy import dot
from numpy.linalg import norm
from django.urls import reverse

@login_required
def main(request):
    user_pets = Pet.objects.filter(owner=request.user)
    preference_fields = [
        ('통원치료비', 'outpatient'),
        ('입원치료비', 'inpatient'),
        ('수술치료비', 'surgery'),
        ('배상책임', 'liability'),
        ('슬관절', 'joint'),
        ('피부병', 'skin'),
        ('구강질환', 'oral'),
        ('비뇨기질환', 'urinary'),
    ]
    context = {
        'user_pets': user_pets,
        'preference_fields': preference_fields,
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
def recommend_form(request, pet_profile_id):
    # preference_fields 정의 (label, key)
    preference_fields = [
        ('통원치료비', 'outpatient'),
        ('입원치료비', 'inpatient'),
        ('수술치료비', 'surgery'),
        ('배상책임', 'liability'),
        ('슬관절', 'joint'),
        ('피부병', 'skin'),
        ('구강질환', 'oral'),
        ('비뇨기질환', 'urinary'),
    ]
    preference_dict = {key: 3 for label, key in preference_fields}
    context = {
        'pet_profile_id': pet_profile_id,
        'preference_fields': preference_fields,
        'preference_dict': preference_dict,
    }
    return render(request, 'insurance/recommend_form.html', context)

@login_required
def insurance_recommend(request, pet_profile_id):
    # POST 데이터가 없으면 폼으로 리다이렉트
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('insurance:recommend_form', args=[pet_profile_id]))
    pet = get_object_or_404(Pet, id=pet_profile_id, owner=request.user)

    # 모든 보험 상품 가져오기
    products = InsuranceProduct.objects.all()

    # 한글 key → 영문 코드 매핑
    preference_map = {
        '통원': 'outpatient',
        '입원': 'inpatient',
        '수술': 'surgery',
        '배상책임': 'liability',
        '슬관절': 'joint',
        '피부병': 'skin',
        '구강질환': 'oral',
        '비뇨기질환': 'urinary',
    }

    # all_coverage_keys를 preference_map의 key만으로 제한
    all_coverage_keys = list(preference_map.keys())

    # preference_fields 정의 (label, key)
    preference_fields = [
        ('통원치료비', 'outpatient'),
        ('입원치료비', 'inpatient'),
        ('수술치료비', 'surgery'),
        ('배상책임', 'liability'),
        ('슬관절', 'joint'),
        ('피부병', 'skin'),
        ('구강질환', 'oral'),
        ('비뇨기질환', 'urinary'),
    ]

    if request.method == 'POST':
        preference_dict = {}
        for label, key in preference_fields:
            preference_dict[key] = int(request.POST.get(key, 3))
    else:
        preference_dict = {key: 3 for label, key in preference_fields}

    # user_vector를 all_coverage_keys의 한글 key를 preference_map(한글→영문)으로 변환해서 preference_dict에서 값을 가져오도록 수정
    user_vector = []
    for cov_key in all_coverage_keys:
        eng_key = preference_map.get(cov_key)
        if eng_key:
            user_vector.append(preference_dict.get(eng_key, 0))
        else:
            user_vector.append(0)

    # cover_type → 카테고리명 매핑
    cover_type_to_category = {
        1: '통원',
        2: '입원',
        3: '수술',
        4: '슬관절',
        5: '피부병',
        6: '구강질환',
        7: '비뇨기질환',
        8: '배상책임',
    }

    # cover.json에서 보장 ID → cover_type 매핑 생성
    cover_id_to_type = {}
    cover_path = Path(__file__).parent / 'fixtures' / 'cover.json'
    if cover_path.exists():
        with open(cover_path, encoding='utf-8') as f:
            for item in json.load(f):
                cover_id_to_type[item['pk']] = item['fields']['cover_type']

    def get_category_coverage_vector(coverage_details, all_coverage_keys):
        vector = [0 for _ in all_coverage_keys]
        # 1. 카테고리 key가 있으면 1
        for idx, key in enumerate(all_coverage_keys):
            if key in coverage_details:
                vector[idx] = 1
        # 2. '기본보장', '특별보장'의 보장 ID로 카테고리 체크
        for section in ['기본보장', '특별보장']:
            for cover_id in coverage_details.get(section, []):
                cover_type = cover_id_to_type.get(cover_id)
                category = cover_type_to_category.get(cover_type)
                if category and category in all_coverage_keys:
                    idx = all_coverage_keys.index(category)
                    vector[idx] = 1
        # 3. 질병보장(disease) 항목도 기존대로 체크
        disease_dict = coverage_details.get('질병보장', {})
        for disease in disease_dict.values():
            cover_type = disease.get('cover_type')
            if cover_type and cover_type_to_category.get(cover_type) in all_coverage_keys:
                idx = all_coverage_keys.index(cover_type_to_category[cover_type])
                vector[idx] = 1
        return vector

    # cosine similarity 함수 정의
    def cosine_similarity(a, b):
        if norm(a) == 0 or norm(b) == 0:
            return 0.0
        return float(dot(a, b) / (norm(a) * norm(b)))

    before_ranking = []
    for product in products:
        product_vector = get_category_coverage_vector(product.coverage_details, all_coverage_keys)
        # product_vector: 0/1, user_vector: 1~5점
        matching_score = cosine_similarity(user_vector, product_vector)
        temp_detail = {}
        temp_detail['product'] = product
        temp_detail['company_score'] = float(product.company.rating) if product.company and product.company.rating else 0.0
        details = getattr(product, 'insurancedetail_set', None)
        if details and details.exists():
            price_score = float(details.aggregate(models.Avg('price_score'))['price_score__avg'] or 0)
        else:
            price_score = float(product.base_price)
        temp_detail['price_score'] = price_score
        temp_detail['matching_score'] = matching_score
        temp_detail['cover_count'] = len(flatten_coverage_keys(product.coverage_details))
        temp_detail['sure_score'] = make_sure_score(temp_detail['company_score'], price_score, matching_score)
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
        if hasattr(product, 'special_benefits') and isinstance(product.special_benefits, list):
            product.special_benefits = [cover_map.get(i, str(i)) for i in product.special_benefits]
        before_ranking.append(temp_detail)

    sure_ranking = sorted(before_ranking, key=lambda item: -item['sure_score'])
    price_ranking = sorted(before_ranking, key=lambda item: item['price_score'])
    cover_ranking = sorted(before_ranking, key=lambda item: -item['cover_count'])

    # 디버깅용 print: user_vector와 추천 결과
    print('user_vector:', user_vector)
    for item in sure_ranking:
        print(getattr(item['product'], 'insurance_name', None) or getattr(item['product'], 'name', None), item['matching_score'], item['sure_score'])

    print('all_coverage_keys:', all_coverage_keys)
    if products:
        print('샘플 coverage_details:', products[0].insurance_name, products[0].coverage_details)

    context = {
        'pet': pet,
        'sure_ranking': sure_ranking,
        'price_ranking': price_ranking,
        'cover_ranking': cover_ranking,
        'preference_fields': preference_fields,
        'preference_dict': preference_dict,
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

    products = InsuranceProduct.objects.all()

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

    # 비교에서도 선호도 기반 user_vector 생성
    preference_fields = [
        ('통원치료비', 'outpatient'),
        ('입원치료비', 'inpatient'),
        ('수술치료비', 'surgery'),
        ('배상책임', 'liability'),
        ('슬관절', 'joint'),
        ('피부병', 'skin'),
        ('구강질환', 'oral'),
        ('비뇨기질환', 'urinary'),
    ]
    preference_map = {
        '통원': 'outpatient',
        '입원': 'inpatient',
        '수술': 'surgery',
        '배상책임': 'liability',
        '슬관절': 'joint',
        '피부병': 'skin',
        '구강질환': 'oral',
        '비뇨기질환': 'urinary',
    }
    all_coverage_keys = list(preference_map.keys())
    # POST로 선호도 값이 오면 반영
    if request.method == 'POST':
        preference_dict = {}
        for label, key in preference_fields:
            preference_dict[key] = int(request.POST.get(key, 3))
        user_vector = [preference_dict.get(preference_map[k], 3) for k in all_coverage_keys]
    else:
        user_vector = [3 for _ in all_coverage_keys]

    # cover_type_to_category, cover_id_to_type 등 기존 추천과 동일하게 적용
    cover_type_to_category = {
        1: '통원', 2: '입원', 3: '수술', 4: '슬관절', 5: '피부병', 6: '구강질환', 7: '비뇨기질환', 8: '배상책임',
    }
    cover_id_to_type = {}
    if cover_path.exists():
        with open(cover_path, encoding='utf-8') as f:
            for item in json.load(f):
                cover_id_to_type[item['pk']] = item['fields']['cover_type']
    def get_category_coverage_vector(coverage_details, all_coverage_keys):
        vector = [0 for _ in all_coverage_keys]
        for idx, key in enumerate(all_coverage_keys):
            if key in coverage_details:
                vector[idx] = 1
        for section in ['기본보장', '특별보장']:
            for cover_id in coverage_details.get(section, []):
                cover_type = cover_id_to_type.get(cover_id)
                category = cover_type_to_category.get(cover_type)
                if category and category in all_coverage_keys:
                    idx = all_coverage_keys.index(category)
                    vector[idx] = 1
        disease_dict = coverage_details.get('질병보장', {})
        for disease in disease_dict.values():
            cover_type = disease.get('cover_type')
            if cover_type and cover_type_to_category.get(cover_type) in all_coverage_keys:
                idx = all_coverage_keys.index(cover_type_to_category[cover_type])
                vector[idx] = 1
        return vector
    def cosine_similarity(a, b):
        from numpy import dot
        from numpy.linalg import norm
        if norm(a) == 0 or norm(b) == 0:
            return 0.0
        return float(dot(a, b) / (norm(a) * norm(b)))

    processed = []
    for product in products:
        product.coverage_details_verbose = {}
        for key, value in product.coverage_details.items():
            if isinstance(value, list):
                product.coverage_details_verbose[key] = [cover_map.get(i) or disease_map.get(i) or str(i) for i in value]
            else:
                product.coverage_details_verbose[key] = value
        if not isinstance(product.special_benefits, list):
            product.special_benefits = []
        else:
            product.special_benefits = [cover_map.get(i) or disease_map.get(i) or str(i) for i in product.special_benefits]
        company_score = float(product.company.rating) if product.company and product.company.rating else 0.0
        details = getattr(product, 'insurancedetail_set', None)
        if details and details.exists():
            price_score = float(details.aggregate(models.Avg('price_score'))['price_score__avg'] or 0)
        else:
            price_score = float(product.base_price)
        product_vector = get_category_coverage_vector(product.coverage_details, all_coverage_keys)
        matching_score = cosine_similarity(user_vector, product_vector)
        sure_score = make_sure_score(company_score, price_score, matching_score)
        processed.append((product, sure_score))

    context = {
        'products': processed,
        'coverage_keys': all_coverage_keys,
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
