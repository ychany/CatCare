from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Pet(models.Model):
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

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100, verbose_name='이름')
    breed = models.CharField(max_length=20, choices=CAT_BREEDS, verbose_name='종')
    birth_date = models.DateField(verbose_name='생년월일')
    image = models.ImageField(upload_to='pet_images/', verbose_name='프로필 사진', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_breed_display()})"

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
