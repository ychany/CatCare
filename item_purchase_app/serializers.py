from rest_framework import serializers
from .models import OtherPurchase

class OtherPurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherPurchase
        fields = '__all__'
        read_only_fields = ('user', 'cat', 'created_at', 'updated_at') 