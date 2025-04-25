import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
from .models import PetProfile, InsuranceChoice, InsuranceProduct
from datetime import datetime, timedelta

def load_user_data(pet_type):
    """반려동물 종류별 사용자 데이터 로드"""
    try:
        if pet_type == 'dog':
            df = pd.read_csv('insurance_app/knn_data/doguser.csv')
        else:
            df = pd.read_csv('insurance_app/knn_data/catuser.csv')
        return df
    except FileNotFoundError:
        # 데이터 파일이 없는 경우 빈 데이터프레임 반환
        return pd.DataFrame()

def calculate_euclidean_distance(user, neighbor):
    """유클리드 거리 계산"""
    distance = 0
    for key in ['age', 'weight', 'medical_history']:
        if key in user and key in neighbor:
            distance += (user[key] - neighbor[key]) ** 2
    return np.sqrt(distance)

def calculate_inverse_weight(distance):
    """역거리 가중치 계산"""
    return 1 / (distance + 1e-10)  # 0으로 나누기 방지

def get_nearest_neighbors(user_profile, k=5):
    """가장 가까운 k개의 이웃 찾기"""
    # 사용자 프로필의 특성 추출
    pet_type = user_profile.pet_type
    age = user_profile.get_age()
    weight = user_profile.weight if user_profile.weight else 0
    
    # 모든 보험 상품 가져오기
    all_products = InsuranceProduct.objects.filter(pet_type=pet_type)
    
    # 각 상품과의 유사도 계산
    similarities = []
    for product in all_products:
        # 상품의 특성 추출
        min_age = product.min_age or 0
        max_age = product.max_age or 100
        min_weight = product.min_weight or 0
        max_weight = product.max_weight or 100
        
        # 유사도 계산
        age_similarity = 1 if min_age <= age <= max_age else 0
        
        # weight가 None이거나 weight 제한이 없는 경우 weight_similarity는 1
        if product.min_weight is None or product.max_weight is None:
            weight_similarity = 1
        else:
            weight_similarity = 1 if min_weight <= weight <= max_weight else 0
        
        # 나이와 체중의 유사도를 평균내어 총 유사도 계산
        total_similarity = (age_similarity + weight_similarity) / 2
        
        # 보험 상품의 sure_index도 고려 (sure_index가 None인 경우 0.5 사용)
        sure_index = product.sure_index if product.sure_index is not None else 0.5
        total_similarity = (total_similarity + sure_index) / 2
        
        similarities.append((product, total_similarity))
    
    # 유사도 기준으로 정렬
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # 상위 k개 상품 반환
    return [item[0] for item in similarities[:k]]

def predict_insurance(user_profile, k=5):
    """KNN을 사용하여 보험 상품 추천"""
    # 가장 가까운 k개의 이웃 찾기
    neighbors = get_nearest_neighbors(user_profile, k)
    
    if not neighbors:
        return []
    
    # 이웃들이 선택한 보험 상품의 가중치 계산
    weights = {}
    for neighbor in neighbors:
        if neighbor.id not in weights:
            weights[neighbor.id] = 0
        weights[neighbor.id] += 1
    
    # 가중치 기준으로 정렬
    sorted_products = sorted(weights.items(), key=lambda x: x[1], reverse=True)
    
    # 상위 5개 상품 반환
    return [InsuranceProduct.objects.get(id=product_id) for product_id, _ in sorted_products[:5]]

def update_user_choice(pet_profile, insurance_product):
    """사용자의 보험 선택 기록 업데이트"""
    InsuranceChoice.objects.create(
        pet_profile=pet_profile,
        insurance_product=insurance_product,
        monthly_premium=insurance_product.base_price,
        start_date=datetime.now().date(),
        end_date=datetime.now().date() + timedelta(days=365),
        is_active=True
    ) 