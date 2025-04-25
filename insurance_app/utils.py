from datetime import datetime
from .models import InsuranceProduct
import numpy as np

def calculate_age(birth_date):
    today = datetime.now().date()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def calculate_sure_index(product, pet_type, age):
    # 기본 점수
    base_score = 0
    
    # 보험사 신뢰도 점수 (0.0 ~ 1.0)
    company_score = product.company.rating / 5.0
    
    # 나이에 따른 가중치
    age_weight = 1.0
    if age < 1:
        age_weight = 0.8
    elif age > 10:
        age_weight = 0.6
    
    # 보장 내용 점수
    coverage_score = 0
    coverage_details = product.coverage_details
    
    # 기본 보장 항목 점수
    basic_coverage = ['통원치료비', '입원치료비', '수술치료비']
    for item in basic_coverage:
        if item in coverage_details and coverage_details[item]:
            coverage_score += 0.2
    
    # 특별 보장 항목 점수
    special_coverage = {
        'dog': ['슬관절', '피부병'],
        'cat': ['비뇨기', '구강']
    }
    
    for item in special_coverage.get(pet_type, []):
        if item in coverage_details and coverage_details[item]:
            coverage_score += 0.3
    
    # SURE 지수 계산
    sure_index = (company_score * 0.4 + coverage_score * 0.6) * age_weight
    
    return sure_index

def recommend_insurance(pet_type, birth_date, weight=None):
    age = calculate_age(birth_date)
    products = InsuranceProduct.objects.all()
    
    # 각 상품의 SURE 지수 계산
    product_scores = []
    for product in products:
        # 나이와 체중 조건 확인
        if (product.min_age and age < product.min_age) or (product.max_age and age > product.max_age):
            continue
        if weight and ((product.min_weight and weight < product.min_weight) or (product.max_weight and weight > product.max_weight)):
            continue
            
        sure_index = calculate_sure_index(product, pet_type, age)
        product_scores.append((product, sure_index))
    
    # SURE 지수 기준으로 정렬
    product_scores.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 3개 상품 반환
    return [product for product, _ in product_scores[:3]] 