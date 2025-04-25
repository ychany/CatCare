from django.core.management.base import BaseCommand
from insurance_app.models import InsuranceCompany, InsuranceProduct
import json
import os
import random

class Command(BaseCommand):
    help = 'Import insurance data from local fixtures'

    def handle(self, *args, **kwargs):
        # 파일 경로 설정
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        fixtures_dir = os.path.join(base_dir, 'insurance_app', 'fixtures')

        # 보험사 데이터 가져오기
        with open(os.path.join(fixtures_dir, 'insurance.json'), 'r', encoding='utf-8') as f:
            insurance_data = json.load(f)

        # 보험 상세 데이터 가져오기
        with open(os.path.join(fixtures_dir, 'insurance_detail.json'), 'r', encoding='utf-8') as f:
            insurance_detail_data = json.load(f)

        # 질병 데이터 가져오기
        with open(os.path.join(fixtures_dir, 'disease.json'), 'r', encoding='utf-8') as f:
            disease_data = json.load(f)

        # 보험사 및 기본 상품 생성
        for item in insurance_data:
            # 보험사 평점과 고객 만족도를 랜덤하게 생성 (3.5 ~ 5.0 사이)
            rating = round(random.uniform(3.5, 5.0), 1)
            satisfaction = round(random.uniform(3.5, 5.0), 1)

            company, created = InsuranceCompany.objects.get_or_create(
                name=item['fields']['company_name'],
                defaults={
                    'rating': rating,
                    'customer_satisfaction': satisfaction,
                    'website': item['fields']['company_url'],
                    'description': item['fields'].get('content', '') + '\n' + item['fields'].get('etc', ''),
                }
            )

            # 보험 상품 생성
            product, created = InsuranceProduct.objects.get_or_create(
                company=company,
                name=item['fields']['insurance_name'],
                defaults={
                    'pet_type': 'dog' if item['fields']['species'] == 1 else 'cat',
                    'base_price': 50000,
                    'min_age': 0,
                    'max_age': 20,
                    'coverage_period': item['fields']['payment_period'],
                    'renewal_cycle': item['fields']['payment_period'],
                    'coverage_details': {
                        '입원': '입원 시 발생하는 치료비',
                        '수술': '수술 시 발생하는 치료비',
                        '통원': '통원 치료 시 발생하는 치료비',
                        '약제비': '처방된 약제비용',
                        '검사비': '각종 검사 비용'
                    },
                    'coverage_limits': {
                        '입원': '300만원',
                        '수술': '200만원',
                        '통원': '15만원',
                        '약제비': '10만원',
                        '검사비': '20만원'
                    },
                    'special_benefits': ['24시간 상담 서비스', '예방접종 할인', '정기검진 할인']
                }
            )

            # 보험 상세 정보 업데이트
            for detail in insurance_detail_data:
                if detail['fields']['insurance'] == item['pk']:
                    product.base_price = detail['fields']['fee']
                    
                    coverage_details = {}
                    if detail['fields'].get('basic'):
                        coverage_details['기본보장'] = detail['fields']['basic']
                    if detail['fields'].get('special'):
                        coverage_details['특별보장'] = detail['fields']['special']
                    
                    # 질병 정보 추가
                    disease_coverage = {}
                    for disease in disease_data:
                        if disease['fields'].get('cover_type'):
                            disease_coverage[disease['fields']['name']] = {
                                '정보': disease['fields']['info'],
                                '팁': disease['fields']['tip'],
                                '원인': disease['fields']['cause']
                            }
                    coverage_details['질병보장'] = disease_coverage
                    
                    product.coverage_details = coverage_details
                    product.special_benefits = detail['fields'].get('special', {})
                    product.coverage_limits = detail['fields'].get('all_cover', {})
                    product.save()

        self.stdout.write(self.style.SUCCESS('Successfully imported insurance data')) 