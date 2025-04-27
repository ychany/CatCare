from rest_framework import serializers
from .models import OtherPurchase
from common_app.models import Pet

class PetSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        fields = ('id', 'name')

class OtherPurchaseSerializer(serializers.ModelSerializer):
    cat = PetSimpleSerializer(read_only=True)
    class Meta:
        model = OtherPurchase
        fields = '__all__'
        read_only_fields = ('user', 'cat', 'created_at', 'updated_at') 