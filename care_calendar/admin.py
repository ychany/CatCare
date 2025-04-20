from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('category', 'pet', 'start_time', 'user')
    list_filter = ('category', 'pet', 'user')
    search_fields = ('description', 'pet__name')
    date_hierarchy = 'start_time'
