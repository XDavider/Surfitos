import requests
import pytz
from datetime import date, datetime
from django.utils.timezone import make_aware
from .models import (
    MarineDailyData, MarineHourlyData,
    WeatherDailyData, WeatherHourlyData
)

# === Función para guardar datos de Marine ===
def fetch_and_save_marine_data(playa):
    lat = playa.latitud
    lon = playa.longitud
    url = (
        f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
        f"&daily=wave_height_max,wave_direction_dominant,wave_period_max,swell_wave_height_max,swell_wave_direction_dominant,swell_wave_period_max"
        f"&hourly=wave_height,wave_direction,wave_period,swell_wave_height,swell_wave_direction,swell_wave_period"
        f"&forecast_days=1"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    fecha = date.fromisoformat(data["daily"]["time"][0])

    # Guardar daily
    MarineDailyData.objects.update_or_create(
        playa=playa,
        fecha=fecha,
        defaults={
            'wave_height_max': data['daily']['wave_height_max'][0],
            'wave_direction_dominant': data['daily']['wave_direction_dominant'][0],
            'wave_period_max': data['daily']['wave_period_max'][0],
            'swell_wave_height_max': data['daily']['swell_wave_height_max'][0],
            'swell_wave_direction_dominant': data['daily']['swell_wave_direction_dominant'][0],
            'swell_wave_period_max': data['daily']['swell_wave_period_max'][0],
        }
    )

    # Guardar hourly
    times = data['hourly']['time']
    for i, ts in enumerate(times):
        timestamp = make_aware(datetime.fromisoformat(ts))
        MarineHourlyData.objects.update_or_create(
            playa=playa,
            timestamp=timestamp,
            defaults={
                'wave_height': data['hourly']['wave_height'][i],
                'wave_direction': data['hourly']['wave_direction'][i],
                'wave_period': data['hourly']['wave_period'][i],
                'swell_wave_height': data['hourly']['swell_wave_height'][i],
                'swell_wave_direction': data['hourly']['swell_wave_direction'][i],
                'swell_wave_period': data['hourly']['swell_wave_period'][i],
            }
        )


# === Función para guardar datos de Weather ===
def fetch_and_save_weather_data(playa):
    lat = playa.latitud
    lon = playa.longitud
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset"
        f"&hourly=temperature_2m,apparent_temperature,weather_code"
        f"&forecast_days=1"
    )
    response = requests.get(url)
    if response.status_code != 200:
        return

    data = response.json()
    fecha = date.fromisoformat(data['daily']['time'][0])
    europe_madrid = pytz.timezone("Europe/Madrid")
    sunrise = make_aware(datetime.fromisoformat(data['daily']['sunrise'][0]), timezone=pytz.utc).astimezone(
        europe_madrid)
    sunset = make_aware(datetime.fromisoformat(data['daily']['sunset'][0]), timezone=pytz.utc).astimezone(europe_madrid)

    # Guardar daily
    WeatherDailyData.objects.update_or_create(
        playa=playa,
        fecha=fecha,
        defaults={
            'temperature_max': data['daily']['temperature_2m_max'][0],
            'temperature_min': data['daily']['temperature_2m_min'][0],
            'sunrise': sunrise,
            'sunset': sunset,
        }
    )

    # Guardar hourly
    times = data['hourly']['time']
    for i, ts in enumerate(times):
        timestamp = make_aware(datetime.fromisoformat(ts))
        WeatherHourlyData.objects.update_or_create(
            playa=playa,
            timestamp=timestamp,
            defaults={
                'temperature': data['hourly']['temperature_2m'][i],
                'apparent_temperature': data['hourly']['apparent_temperature'][i],
                'weather_code': data['hourly']['weather_code'][i],
            }
        )
