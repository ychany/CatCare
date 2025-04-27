from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Event
from .serializers import EventSerializer
from common_app.models import Pet
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Event.objects.filter(pet__owner=self.request.user)

    def perform_create(self, serializer):
        # 고양이 소유자 확인
        pet = Pet.objects.get(id=self.request.data.get('pet'))
        if pet.owner != self.request.user:
            raise permissions.PermissionDenied("You don't have permission to create events for this pet.")
        serializer.save()

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

@ensure_csrf_cookie
@login_required
def calendar_view(request):
    pets = Pet.objects.filter(owner=request.user)
    # 각 반려동물별 최신 이벤트(진료/접종) 조회
    last_events = {}
    for pet in pets:
        last_event = Event.objects.filter(pet=pet).order_by('-date').first()
        last_events[pet.id] = last_event
    return render(request, 'calendar_app/calendar.html', {'pets': pets, 'last_events': last_events})
