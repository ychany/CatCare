from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Event
from common_app.models import Pet
from datetime import datetime
import json

@login_required
def care_calendar(request):
    """케어 캘린더 메인 페이지를 렌더링합니다."""
    pets = Pet.objects.filter(owner=request.user)
    return render(request, 'care_calendar/care_calendar.html', {'pets': pets})

@login_required
def get_events(request):
    """사용자의 케어 이벤트를 JSON 형식으로 반환합니다."""
    try:
        events = Event.objects.filter(pet__owner=request.user)
        event_list = []
        
        for event in events:
            event_list.append({
                'id': event.id,
                'title': event.get_category_display(),
                'start': event.start_time.isoformat(),
                'description': event.description,
                'pet_id': event.pet.id,
                'pet_name': event.pet.name,
                'category': event.category
            })

        return JsonResponse(event_list, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def create_event(request):
    """새로운 케어 이벤트를 생성합니다."""
    try:
        data = json.loads(request.body)
        
        # 필수 필드 확인
        if not all(k in data for k in ['pet_id', 'start', 'category']):
            return JsonResponse({
                'status': 'error',
                'message': '필수 필드가 누락되었습니다.'
            }, status=400)
            
        pet = get_object_or_404(Pet, id=data['pet_id'], owner=request.user)
        start_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
        
        event = Event.objects.create(
            user=request.user,
            pet=pet,
            start_time=start_date,
            description=data.get('description', ''),
            category=data['category']
        )
        
        response_data = {
            'status': 'success',
            'event': {
                'id': event.id,
                'title': event.get_category_display(),
                'start': event.start_time.isoformat(),
                'description': event.description,
                'pet_id': event.pet.id,
                'pet_name': event.pet.name,
                'category': event.category
            }
        }
        return JsonResponse(response_data)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': f'날짜 형식이 잘못되었습니다: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def update_event(request, event_id):
    """기존 케어 이벤트를 수정합니다."""
    try:
        event = get_object_or_404(Event, id=event_id, user=request.user)
        data = json.loads(request.body)

        # 필수 필드 확인
        if not all(k in data for k in ['pet_id', 'start', 'category']):
            return JsonResponse({
                'status': 'error',
                'message': '필수 필드가 누락되었습니다.'
            }, status=400)
            
        pet = get_object_or_404(Pet, id=data['pet_id'], owner=request.user)
        start_date = datetime.strptime(data['start'], '%Y-%m-%d').date()
        
        event.pet = pet
        event.start_time = start_date
        event.description = data.get('description', '')
        event.category = data['category']
        event.save()
        
        response_data = {
            'status': 'success',
            'message': '이벤트가 성공적으로 수정되었습니다.',
            'event': {
                'id': event.id,
                'title': event.get_category_display(),
                'start': event.start_time.isoformat(),
                'description': event.description,
                'pet_id': event.pet.id,
                'pet_name': event.pet.name,
                'category': event.category
            }
        }
        return JsonResponse(response_data, status=200)
    except json.JSONDecodeError as e:
        return JsonResponse({
            'status': 'error',
            'message': '잘못된 JSON 형식입니다.'
        }, status=400)
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': f'날짜 형식이 잘못되었습니다: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required
@require_http_methods(["DELETE"])
def delete_event(request, event_id):
    """케어 이벤트를 삭제합니다."""
    try:
        event = get_object_or_404(Event, id=event_id, user=request.user)
        event.delete()
        return JsonResponse({
            'status': 'success',
            'message': '이벤트가 삭제되었습니다.'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

@login_required
def get_previous_care(request, pet_id, category):
    """특정 펫의 특정 카테고리 이전 케어 기록을 가져옵니다."""
    try:
        # 현재 날짜 기준으로 가장 최근 이벤트를 가져옴
        today = timezone.now().date()
        
        event = Event.objects.filter(
            pet_id=pet_id,
            category=category,
        ).order_by('-start_time').first()  # 가장 최근 날짜순으로 정렬하여 첫 번째 항목 가져오기

        
        if event:
            formatted_date = event.start_time.strftime('%Y-%m-%d')
            
            response_data = {
                'status': 'success',
                'previous_care': {
                    'date': formatted_date,
                    'description': event.description or '',
                    'category': event.category
                }
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'status': 'success',
                'previous_care': None
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
