from django.shortcuts import render
from django.http import JsonResponse
from .models import VetHospital
import json
from common_app.models import Pet

# Create your views here.

def hospital_list(request):
    hospitals = VetHospital.objects.all()
    hospitals_json = json.dumps([
        {
            "name": h.name,
            "address": h.address,
            "phone": h.phone,
            "is_24hours": h.is_24hours,
            "latitude": h.latitude,
            "longitude": h.longitude,
        } for h in hospitals
    ])
    # 로그인한 유저의 고양이만 전달 (또는 전체)
    pets = Pet.objects.filter(owner=request.user) if request.user.is_authenticated else []
    return render(request, 'emergency_app/hospitals.html', {'hospitals': hospitals_json, 'pets': pets})
