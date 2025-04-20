from django.db import models
from common_app.models import Pet

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('vacc', '예방접종'),
        ('med', '진료기록')
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=4, choices=EVENT_TYPE_CHOICES)
    date = models.DateField()
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    next_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.pet.name} ({self.date})"
