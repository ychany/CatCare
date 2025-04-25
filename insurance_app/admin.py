from django.contrib import admin
from .models import InsuranceCompany, InsuranceProduct, InsuranceReview

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'created_at']
    search_fields = ['name']

@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'base_price', 'created_at']
    list_filter = ['company']
    search_fields = ['name', 'company__name']

@admin.register(InsuranceReview)
class InsuranceReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['product', 'rating']
    search_fields = ['product__name', 'user__username']
