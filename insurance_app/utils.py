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
    
    # 상위 3개 상품 (상품, sure_index) 튜플로 반환
    return product_scores[:3]

def euclidean_distance(user, neighbor):
    """유클리드 거리 계산"""
    distance = 0.0
    for i in range(len(user)):
        distance += (user[i] - neighbor[i]) ** 2
    return np.sqrt(distance)

def inverse_weight(user, neighbor):
    """역거리 가중치 계산"""
    num = 1.0
    const = 0.1
    distance = euclidean_distance(user, neighbor)
    return num / (distance + const)

def get_neighbors(user, neighbor_list, k):
    distances = []
    for neighbor in neighbor_list:
        dist = inverse_weight(user, neighbor)
        distances.append((neighbor, dist))
    distances.sort(reverse=True, key=lambda tup: tup[1])
    near_neighbors = []
    for i in range(min(k, len(distances))):
        near_neighbors.append(distances[i][0])
    return near_neighbors

def predict_classification(user, neighbor_list, k):
    neighbors = get_neighbors(user, neighbor_list, k)
    predict_candidate = [row[-1] for row in neighbors]
    return predict_candidate

def get_pred(user, neighbor_list, k):
    predict_candidate = predict_classification(user, neighbor_list, k)
    weight_dist = 0
    for neighbor in neighbor_list:
        weight_dist = inverse_weight(user, neighbor)
    lst = [0] * 100  # 보험상품 개수에 맞게 조정 필요
    for i in range(min(k, len(predict_candidate))):
        x = predict_candidate[i]
        lst[x] += weight_dist
    return lst

def make_sure_score(company_score, price_score, matching_score):
    """SURE 점수(신뢰지수) 가중합 계산"""
    return (company_score * 0.3) + (price_score * 0.3) + (matching_score * 0.4)

def get_coverage_vector(coverage_details, all_coverage_keys):
    """보장항목 딕셔너리를 전체 보장항목 키 기준 벡터(0/1)로 변환"""
    return [1 if key in coverage_details and coverage_details[key] else 0 for key in all_coverage_keys]

def jaccard_similarity(vec1, vec2):
    """자카드 유사도 계산 (0~1)"""
    set1 = set([i for i, v in enumerate(vec1) if v])
    set2 = set([i for i, v in enumerate(vec2) if v])
    if not set1 and not set2:
        return 1.0  # 둘 다 비어있으면 완전 일치로 간주
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def flatten_coverage_keys(coverage_details):
    keys = set()
    for k, v in coverage_details.items():
        if isinstance(v, list):
            keys.update(v)
        elif isinstance(v, dict):
            keys.update(v.keys())
    return keys

def get_flat_coverage_vector(coverage_details, all_coverage_keys):
    keys = flatten_coverage_keys(coverage_details)
    return [1 if key in keys else 0 for key in all_coverage_keys]

# price_score, matching_score 등은 실제 데이터와 연동하여 views.py에서 계산/전달하도록 설계 