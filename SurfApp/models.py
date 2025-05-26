from django.db import models

# === Datos de las playas ===
class Playa(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.CharField(max_length=100)
    latitud = models.FloatField()
    longitud = models.FloatField()

    def __str__(self):
        return f"{self.nombre} - {self.lugar}"


# === Datos diarios de la API Marine ===
class MarineDailyData(models.Model):
    playa = models.ForeignKey(Playa, on_delete=models.CASCADE)
    fecha = models.DateField()

    wave_height_max = models.FloatField(null=True)
    wave_direction_dominant = models.FloatField(null=True)
    wave_period_max = models.FloatField(null=True)

    swell_wave_height_max = models.FloatField(null=True)
    swell_wave_direction_dominant = models.FloatField(null=True)
    swell_wave_period_max = models.FloatField(null=True)

    class Meta:
        unique_together = ('playa', 'fecha')


# === Datos por hora de la API Marine ===
class MarineHourlyData(models.Model):
    playa = models.ForeignKey(Playa, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    wave_height = models.FloatField(null=True)
    wave_direction = models.FloatField(null=True)
    wave_period = models.FloatField(null=True)

    swell_wave_height = models.FloatField(null=True)
    swell_wave_direction = models.FloatField(null=True)
    swell_wave_period = models.FloatField(null=True)

    class Meta:
        unique_together = ('playa', 'timestamp')


# === Datos diarios de la API Weather Forecast ===
class WeatherDailyData(models.Model):
    playa = models.ForeignKey(Playa, on_delete=models.CASCADE)
    fecha = models.DateField()

    temperature_max = models.FloatField(null=True)
    temperature_min = models.FloatField(null=True)
    sunrise = models.DateTimeField(null=True)
    sunset = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('playa', 'fecha')


# === Datos por hora de la API Weather Forecast ===
class WeatherHourlyData(models.Model):
    playa = models.ForeignKey(Playa, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()

    temperature = models.FloatField(null=True)
    apparent_temperature = models.FloatField(null=True)
    weather_code = models.IntegerField(null=True)  # WMO code

    class Meta:
        unique_together = ('playa', 'timestamp')