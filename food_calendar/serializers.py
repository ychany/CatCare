from rest_framework import serializers
from .models import FoodEvent, OtherPurchase

class FoodEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodEvent
        fields = '__all__'

class OtherPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherPurchase
        fields = '__all__'
        read_only_fields = ('user', 'cat', 'created_at', 'updated_at') 