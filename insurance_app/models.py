from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name='보험사명')
    logo = models.ImageField(upload_to='insurance/company_logos/', null=True, blank=True)
    rating = models.FloatField(default=3.0, validators=[MinValueValidator(0.0), MaxValueValidator(5.0)], verbose_name='신뢰도 등급')
    customer_satisfaction = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='고객 만족도')
    contact_number = models.CharField(max_length=20, verbose_name='연락처')
    website = models.URLField(null=True, blank=True, verbose_name='홈페이지')
    description = models.TextField(null=True, blank=True, verbose_name='회사 설명')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '보험사'
        verbose_name_plural = '보험사들'

class InsuranceProduct(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', '강아지'),
        ('cat', '고양이'),
    ]

    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, verbose_name='보험사', related_name='products')
    name = models.CharField(max_length=200, verbose_name='상품명')
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES, verbose_name='동물 종류', default='cat')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='기본 보험료')
    min_age = models.PositiveIntegerField(verbose_name='최소 나이')
    max_age = models.PositiveIntegerField(verbose_name='최대 나이')
    min_weight = models.FloatField(verbose_name='최소 체중', null=True, blank=True)
    max_weight = models.FloatField(verbose_name='최대 체중', null=True, blank=True)
    coverage_period = models.PositiveIntegerField(verbose_name='보장 기간')
    renewal_cycle = models.PositiveIntegerField(verbose_name='갱신 주기')
    coverage_details = models.JSONField(verbose_name='보장 내역')
    coverage_limits = models.JSONField(verbose_name='보장 한도')
    special_benefits = models.JSONField(verbose_name='특별 혜택')
    sure_index = models.FloatField(default=0.0, verbose_name='안전도 지수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"

    class Meta:
        verbose_name = '보험상품'
        verbose_name_plural = '보험상품들'

class InsuranceReview(models.Model):
    RATING_CHOICES = [
        (1, '1점'),
        (2, '2점'),
        (3, '3점'),
        (4, '4점'),
        (5, '5점')
    ]
    
    product = models.ForeignKey(InsuranceProduct, on_delete=models.CASCADE, verbose_name='보험상품')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='평점')
    comment = models.TextField(verbose_name='리뷰내용')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review for {self.product.name}"

    class Meta:
        unique_together = ('product', 'user')
        verbose_name = '보험리뷰'
        verbose_name_plural = '보험리뷰들'

class InsuranceInquiry(models.Model):
    INQUIRY_TYPES = [
        ('price', '보험료 문의'),
        ('coverage', '보장 내용 문의'),
        ('claim', '보험금 청구 문의'),
        ('other', '기타 문의'),
    ]

    PET_TYPES = [
        ('dog', '강아지'),
        ('cat', '고양이'),
    ]

    product = models.ForeignKey(InsuranceProduct, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=10, choices=PET_TYPES)
    pet_age = models.PositiveIntegerField()
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)
    answer = models.TextField(blank=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}님의 {self.product.name} 문의"

    class Meta:
        ordering = ['-created_at']

class PetProfile(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', '개'),
        ('cat', '고양이')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pet_profiles')
    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES)
    breed = models.CharField(max_length=100)
    birth_date = models.DateField()
    weight = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', '수컷'), ('female', '암컷')])
    is_neutered = models.BooleanField(default=False)
    medical_history = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class InsuranceChoice(models.Model):
    pet_profile = models.ForeignKey(PetProfile, on_delete=models.CASCADE, related_name='insurance_choices')
    insurance_product = models.ForeignKey(InsuranceProduct, on_delete=models.CASCADE)
    monthly_premium = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pet_profile.name}'s {self.insurance_product.name}"
