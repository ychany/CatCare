from django.contrib import admin
from .models import VetHospital

@admin.register(VetHospital)
class VetHospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'is_24hours')
    list_filter = ('is_24hours',)
    search_fields = ('name', 'address')
