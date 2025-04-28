from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Pet(models.Model):
    PET_TYPE_CHOICES = [
        ('dog', '강아지'),
        ('cat', '고양이'),
    ]

    CAT_BREEDS = [
        ('persian', '페르시안'),
        ('siamese', '샴'),
        ('maine_coon', '메인쿤'),
        ('ragdoll', '랙돌'),
        ('british', '브리티시 숏헤어'),
        ('scottish', '스코티시 폴드'),
        ('russian', '러시안 블루'),
        ('abyssinian', '아비시니안'),
        ('bengal', '벵갈'),
        ('sphynx', '스핑크스'),
        ('etc', '기타'),
    ]

    DOG_BREEDS = [
        ('poodle', '푸들'),
        ('chihuahua', '치와와'),
        ('shih_tzu', '시츄'),
        ('maltese', '말티즈'),
        ('pomeranian', '포메라니안'),
        ('yorkshire', '요크셔테리어'),
        ('dachshund', '닥스훈트'),
        ('beagle', '비글'),
        ('golden_retriever', '골든 리트리버'),
        ('labrador', '래브라도 리트리버'),
        ('etc', '기타'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100, verbose_name='이름')
    pet_type = models.CharField(max_length=10, choices=PET_TYPE_CHOICES, verbose_name='종류', default='cat')
    breed = models.CharField(max_length=20, verbose_name='품종')
    birth_date = models.DateField(verbose_name='생년월일')
    weight = models.FloatField(verbose_name='체중(kg)', null=True, blank=True)
    image = models.ImageField(upload_to='pet_images/', verbose_name='프로필 사진', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    gender = models.CharField(max_length=10, choices=[('male', '수컷'), ('female', '암컷')], verbose_name='성별', default='male')
    neutered = models.BooleanField(verbose_name='중성화 여부', default=False)
    notes = models.CharField(max_length=255, verbose_name='특이사항', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_pet_type_display()})"

    def get_age(self):
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    def days_until_birthday(self):
        today = date.today()
        next_birthday = date(today.year, self.birth_date.month, self.birth_date.day)
        if next_birthday < today:
            next_birthday = date(today.year + 1, self.birth_date.month, self.birth_date.day)
        return (next_birthday - today).days

    def birthday_progress(self):
        """생일까지 남은 날짜의 진행률을 계산합니다."""
        days_until = self.days_until_birthday()
        # 1년을 100%로 보고 남은 날짜의 비율을 계산
        progress = ((365 - days_until) / 365) * 100
        return round(progress, 1)
