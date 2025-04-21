from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from .models import FoodEvent
from common_app.models import Pet
from django.utils import timezone
from django.db.models import Q

# Create your views here.

@login_required
def food_calendar(request):
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'food_calendar/food_calendar.html', {'pets': pets})

@login_required
def get_events(request, pet_id):
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    # URL 쿼리에서 '+'가 space로 변환되므로 복원
    if start_str:
        start_str = start_str.replace(' ', '+')
    if end_str:
        end_str = end_str.replace(' ', '+')
    try:
        # ISO 포맷 문자열을 datetime 객체로 변환
        start_dt = datetime.fromisoformat(start_str)
        end_dt = datetime.fromisoformat(end_str)
    except Exception:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    end_param = end_str
    # feed(사료)는 개봉부터 종료 전까지 혹은 종료된 경우에도 윈도우 기간에 걸쳐 표시
    events = FoodEvent.objects.filter(
        user=request.user,
        pet_id=pet_id
    ).filter(
        Q(type='feed', end_time__isnull=True, start_time__lte=end_dt)
        | Q(type='feed', end_time__isnull=False, end_time__gte=start_dt, start_time__lte=end_dt)
        | Q(type='snack', start_time__gte=start_dt, start_time__lte=end_dt)
    )
    event_list = []
    for event in events:
        # 사료 이벤트: 개봉일부터 오늘 또는 종료일까지 표시하고, 섭취중이면 제목에 표시
        if event.type == 'feed':
            if event.end_time:
                end_iso = event.end_time.isoformat()
                title = f"🥣 {event.product_name}"
            else:
                end_iso = timezone.now().isoformat()
                title = f"🥣 {event.product_name} (섭취중)"
        else:
            end_iso = event.end_time.isoformat() if event.end_time else None
            title = f"🍖 {event.product_name}"
        event_list.append({
            'id': event.id,
            'title': title,
            'start': event.start_time.isoformat(),
            'end': end_iso,
            'pet_id': event.pet.id,
            'type': event.type,
            'product_name': event.product_name,
            'purchase_link': event.purchase_link,
            'rating': event.rating,
            'previous_food': event.previous_food,
            'quantity_kg': event.quantity_kg,
            'duration_days': event.duration_days,
            'description': event.description,
        })
    return JsonResponse(event_list, safe=False)

@login_required
@require_http_methods(['POST'])
def create_event(request):
    try:
        data = json.loads(request.body)
        pet = get_object_or_404(Pet, id=data.get('pet_id'), owner=request.user)
        
        event = FoodEvent.objects.create(
            user=request.user,
            pet=pet,
            description=data.get('description', ''),
            type=data.get('type', 'feed'),
            product_name=data.get('product_name', ''),
            purchase_link=data.get('purchase_link', ''),
            rating=data.get('rating', 0),
            previous_food=data.get('previous_food', ''),
            quantity_kg=data.get('quantity_kg', 0),
            duration_days=data.get('duration_days', 0),
            start_time=datetime.fromisoformat(data.get('start').replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(data.get('end').replace('Z', '+00:00')) if data.get('end') else None
        )
        
        return JsonResponse({
            'id': event.id,
            'type': event.type,
            'product_name': event.product_name,
            'purchase_link': event.purchase_link,
            'rating': event.rating,
            'previous_food': event.previous_food,
            'quantity_kg': event.quantity_kg,
            'duration_days': event.duration_days,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat() if event.end_time else None,
            'pet_id': event.pet.id,
            'description': event.description,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_event_details(request, event_id):
    event = get_object_or_404(FoodEvent, id=event_id, user=request.user)
    return JsonResponse({
        'id': event.id,
        'type': event.type,
        'product_name': event.product_name,
        'purchase_link': event.purchase_link,
        'rating': event.rating,
        'previous_food': event.previous_food,
        'quantity_kg': event.quantity_kg,
        'duration_days': event.duration_days,
        'start': event.start_time.isoformat(),
        'end': event.end_time.isoformat() if event.end_time else None,
        'pet_id': event.pet.id,
        'description': event.description,
    })

@login_required
@require_http_methods(['DELETE'])
def delete_event(request, event_id):
    event = get_object_or_404(FoodEvent, id=event_id, user=request.user)
    event.delete()
    return JsonResponse({'message': '이벤트가 성공적으로 삭제되었습니다.'})

@login_required
@require_http_methods(["PUT", "PATCH"])
def update_food_event(request, event_id):
    try:
        event = get_object_or_404(FoodEvent, id=event_id, user=request.user)
        data = json.loads(request.body)
        
        if 'description' in data:
            event.description = data['description']
        if 'type' in data:
            event.type = data['type']
        if 'product_name' in data:
            event.product_name = data['product_name']
        if 'purchase_link' in data:
            event.purchase_link = data['purchase_link']
        if 'rating' in data:
            event.rating = data['rating']
        if 'previous_food' in data:
            event.previous_food = data['previous_food']
        if 'quantity_kg' in data:
            event.quantity_kg = data['quantity_kg']
        if 'duration_days' in data:
            event.duration_days = data['duration_days']
        if 'start_time' in data:
            event.start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        if 'end_time' in data:
            event.end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        if 'pet_id' in data:
            event.pet_id = data['pet_id']
            
        event.save()
        return JsonResponse({
            'id': event.id,
            'type': event.type,
            'product_name': event.product_name,
            'purchase_link': event.purchase_link,
            'rating': event.rating,
            'previous_food': event.previous_food,
            'quantity_kg': event.quantity_kg,
            'duration_days': event.duration_days,
            'start_time': event.start_time.isoformat(),
            'end_time': event.end_time.isoformat(),
            'pet_id': event.pet_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(["DELETE"])
def delete_food_event(request, event_id):
    try:
        event = get_object_or_404(FoodEvent, id=event_id, user=request.user)
        event.delete()
        return JsonResponse({'message': '일정이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@require_http_methods(['POST'])
def end_event(request, event_id):
    # 사료 이벤트 종료 및 통계 계산
    event = get_object_or_404(FoodEvent, id=event_id, user=request.user, type='feed')
    if event.end_time is not None:
        return JsonResponse({'error': '이미 종료된 이벤트입니다.'}, status=400)
    end_time = timezone.now()
    event.end_time = end_time
    event.save()

    # 소비 일수 및 평균 계산
    days = (event.end_time - event.start_time).days + 1
    avg_daily = event.quantity_kg / days if days > 0 else 0

    return JsonResponse({
        'id': event.id,
        'end_time': event.end_time.isoformat(),
        'days': days,
        'total_kg': event.quantity_kg,
        'avg_daily': round(avg_daily, 2),
    })
