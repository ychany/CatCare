from django.db import models
from django.contrib.auth.models import User
from common_app.models import Pet

class Weight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='weight_records', null=True, blank=True)
    date = models.DateField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['user', 'pet', 'date']

    def __str__(self):
        return f"{self.user.username} - {self.pet.name} - {self.date}: {self.weight}kg"
