from django.db import models

# Create your models here.

class VetHospital(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    is_24hours = models.BooleanField(default=False)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '동물병원'
        verbose_name_plural = '동물병원 목록'
