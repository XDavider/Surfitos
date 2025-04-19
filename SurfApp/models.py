from django.db import models

# Create your models here.
from django.db import models

class Playa(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return f"{self.nombre} - {self.lugar}"