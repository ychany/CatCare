from django.shortcuts import render
from django.http import JsonResponse
from .models import VetHospital
import json

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
    return render(request, 'emergency_app/hospitals.html', {'hospitals': hospitals_json})
