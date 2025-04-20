from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
    pet_name = serializers.CharField(source='pet.name', read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'pet', 'pet_name', 'event_type', 'date', 'description', 'notes', 'next_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 