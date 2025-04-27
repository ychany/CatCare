from rest_framework import serializers
from .models import FoodEvent
from common_app.models import Pet

class PetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ('id', 'name')

class FoodEventSerializer(serializers.ModelSerializer):
    pet = PetSimpleSerializer(read_only=True)
    class Meta:
        model = FoodEvent
        fields = '__all__' 