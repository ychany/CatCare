from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from common_app.models import Pet

class FoodEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='사용자')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name='반려동물')
    description = models.TextField(verbose_name='메모', blank=True)
    # 사료/간식 타입
    TYPE_CHOICES = [
        ('feed', '사료'),
        ('snack', '간식'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='feed', verbose_name='타입')
    # 상품 정보
    product_name = models.CharField(max_length=200, verbose_name='상품명')
    purchase_link = models.URLField(verbose_name='구매처 링크', blank=True)
    rating = models.PositiveSmallIntegerField(
        verbose_name='만족도',
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    previous_food = models.CharField(max_length=200, verbose_name='이전 사료', blank=True)
    quantity_kg = models.FloatField(verbose_name='구매량(kg)', default=0)
    duration_days = models.PositiveIntegerField(verbose_name='소비 기간(일)', default=0)
    start_time = models.DateTimeField(verbose_name='시작 시간')
    end_time = models.DateTimeField(verbose_name='종료 시간', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-start_time']
        verbose_name = '식사 기록'
        verbose_name_plural = '식사 기록'

    def __str__(self):
        return f'{self.pet.name}의 식사 - {self.start_time}'
