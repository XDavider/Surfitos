from django.db import models

# Create your models here.
from django.db import models

# Modelo que representa una playa en la base de datos
class Playa(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    # Representación en texto del objeto (útil en el admin, logs, etc.)
    def __str__(self):
        return f"{self.nombre} - {self.lugar}"