from rest_framework import serializers
from .models import Weight

class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = ['id', 'pet', 'date', 'weight']
        read_only_fields = ['id'] 