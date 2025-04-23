from django.db import models
from django.contrib.auth.models import User
from common_app.models import Pet

# Create your models here.

# 기타 구매 모델
class OtherPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='사용자')
    cat = models.ForeignKey(Pet, on_delete=models.CASCADE, verbose_name='반려동물')
    purchase_date = models.DateField(verbose_name='구매일')
    price = models.PositiveIntegerField(verbose_name='가격')
    type = models.CharField(max_length=50, verbose_name='타입')
    product_name = models.CharField(max_length=100, verbose_name='상품명')
    purchase_link = models.URLField(verbose_name='구매처 링크', blank=True)
    rating = models.PositiveSmallIntegerField(
        verbose_name='만족도',
        choices=[(i, str(i)) for i in range(1,6)],
        default=0
    )
    memo = models.TextField(verbose_name='메모', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-purchase_date']
        verbose_name = '기타 구매'
        verbose_name_plural = '기타 구매'

    def __str__(self):
        return f'{self.cat.name} 기타 구매 - {self.purchase_date}'
