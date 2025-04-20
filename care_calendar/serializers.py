from rest_framework import serializers
from .models import CareEvent

class CareEventSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    care_type_display = serializers.CharField(source='get_care_type_display', read_only=True)
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = CareEvent
        fields = ['id', 'pet', 'pet_name', 'care_type', 'care_type_display', 
                 'last_date', 'interval', 'unit', 'unit_display', 'next_date', 
                 'created_at', 'updated_at']
        read_only_fields = ['next_date', 'created_at', 'updated_at'] 