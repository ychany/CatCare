from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Weight
from .serializers import WeightSerializer
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
from common_app.models import Pet
import json

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def weight_list(request):
    if request.method == 'GET':
        pet_id = request.GET.get('pet_id')
        weights = Weight.objects.filter(user=request.user)
        if pet_id:
            weights = weights.filter(pet_id=pet_id)
        weights = weights.order_by('-date')
        data = []
        for i, weight in enumerate(weights):
            weight_data = {
                'id': weight.id,
                'pet': weight.pet_id,
                'date': weight.date,
                'weight': float(weight.weight),
                'change': None,
                'days_since_last': None
            }
            
            if i < len(weights) - 1:
                prev_weight = weights[i + 1]
                weight_data['change'] = float(weight.weight) - float(prev_weight.weight)
                weight_data['days_since_last'] = (weight.date - prev_weight.date).days
            
            data.append(weight_data)
        return Response(data)
    
    elif request.method == 'POST':
        serializer = WeightSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def weight_tracker_view(request):
    user_pets = list(Pet.objects.filter(owner=request.user).values('id', 'name')) if request.user.is_authenticated else []
    return render(request, 'weight_tracker/index.html', {'user_pets': json.dumps(user_pets)})
