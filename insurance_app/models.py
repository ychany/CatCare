from django.db import models
from django.conf import settings

class InsuranceCompany(models.Model):
    name = models.CharField(max_length=100, verbose_name='보험사명')
    rating = models.FloatField(verbose_name='신뢰도 등급')
    description = models.TextField(verbose_name='회사 설명')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '보험사'
        verbose_name_plural = '보험사들'

class InsuranceProduct(models.Model):
    company = models.ForeignKey(InsuranceCompany, on_delete=models.CASCADE, verbose_name='보험사')
    name = models.CharField(max_length=200, verbose_name='상품명')
    base_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='기본 보험료')
    coverage_details = models.JSONField(verbose_name='보장 내역')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"

    class Meta:
        verbose_name = '보험상품'
        verbose_name_plural = '보험상품들'

class InsuranceReview(models.Model):
    product = models.ForeignKey(InsuranceProduct, on_delete=models.CASCADE, verbose_name='보험상품')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='사용자')
    rating = models.IntegerField(verbose_name='평점')
    comment = models.TextField(verbose_name='리뷰내용')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')
        verbose_name = '보험리뷰'
        verbose_name_plural = '보험리뷰들'
