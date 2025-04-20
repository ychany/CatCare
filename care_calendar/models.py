from django.db import models
from common_app.models import Pet
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User

class CareEvent(models.Model):
    CARE_TYPE_CHOICES = [
        ('nail', '발톱깎기'),
        ('ear', '귀청소'),
        ('fur', '털정리'),
        ('brush', '양치하기')
    ]
    
    INTERVAL_UNIT_CHOICES = [
        ('day', '일'),
        ('week', '주'),
        ('month', '월')
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='care_schedule_events')
    care_type = models.CharField(max_length=20, choices=CARE_TYPE_CHOICES)
    last_date = models.DateField()
    interval = models.PositiveIntegerField(help_text='주기 간격 숫자')
    unit = models.CharField(max_length=10, choices=INTERVAL_UNIT_CHOICES)
    next_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['next_date']

    def save(self, *args, **kwargs):
        # next_date 자동 계산
        if self.last_date and self.interval and self.unit:
            if self.unit == 'day':
                self.next_date = self.last_date + timedelta(days=self.interval)
            elif self.unit == 'week':
                self.next_date = self.last_date + timedelta(weeks=self.interval)
            elif self.unit == 'month':
                self.next_date = self.last_date + relativedelta(months=self.interval)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_care_type_display()} - {self.pet.name} ({self.next_date})"

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('nail', '발톱깎기'),
        ('ear', '귀청소'),
        ('brush', '양치하기'),
        ('fur', '털정리'),
    ]

    description = models.TextField(blank=True, null=True, verbose_name='설명')
    start_time = models.DateField(verbose_name='시작 날짜')
    end_time = models.DateField(verbose_name='종료 날짜', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='카테고리')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='사용자')
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='calendar_events', verbose_name='고양이')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '일정'
        verbose_name_plural = '일정들'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.get_category_display()} - {self.pet.name}"
