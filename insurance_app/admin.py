from django.contrib import admin
from django.utils.html import format_html
from .models import InsuranceCompany, InsuranceProduct, InsuranceInquiry, InsuranceReview

@admin.register(InsuranceCompany)
class InsuranceCompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'customer_satisfaction', 'contact_number', 'website_link')
    search_fields = ('name',)
    list_filter = ('rating',)
    
    def website_link(self, obj):
        return format_html('<a href="{}" target="_blank">{}</a>', obj.website, obj.website)
    website_link.short_description = '홈페이지'

@admin.register(InsuranceProduct)
class InsuranceProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'base_price', 'min_age', 'max_age', 'sure_index')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')
    readonly_fields = ('sure_index',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('company', 'name', 'base_price', 'sure_index')
        }),
        ('가입 조건', {
            'fields': ('min_age', 'max_age', 'coverage_period', 'renewal_cycle')
        }),
        ('보장 내용', {
            'fields': ('coverage_details', 'coverage_limits', 'special_benefits')
        }),
    )

@admin.register(InsuranceInquiry)
class InsuranceInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'pet_name', 'pet_type', 'inquiry_type', 'created_at', 'is_answered')
    list_filter = ('is_answered', 'inquiry_type', 'pet_type', 'created_at')
    search_fields = ('name', 'email', 'pet_name', 'product__name')
    readonly_fields = ('created_at',)
    actions = ['mark_as_answered']
    
    fieldsets = (
        ('문의 정보', {
            'fields': ('product', 'name', 'email', 'phone', 'created_at')
        }),
        ('반려동물 정보', {
            'fields': ('pet_name', 'pet_type', 'pet_age')
        }),
        ('문의 내용', {
            'fields': ('inquiry_type', 'content')
        }),
        ('답변', {
            'fields': ('is_answered', 'answer', 'answered_at')
        }),
    )
    
    def mark_as_answered(self, request, queryset):
        updated = queryset.update(is_answered=True)
        self.message_user(request, f'{updated}개의 문의가 답변 완료로 표시되었습니다.')
    mark_as_answered.short_description = '선택된 문의를 답변 완료로 표시'

@admin.register(InsuranceReview)
class InsuranceReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'product', 'rating', 'created_at')
        }),
        ('리뷰 내용', {
            'fields': ('comment',)
        }),
    )
