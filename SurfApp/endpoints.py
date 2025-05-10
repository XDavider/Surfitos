import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from .models import Playa
import json

# === Agregar Playa ===
# Permite agregar una playa desde el frontend vía POST con JSON.
# Requiere nombre y lugar; se obtiene latitud y longitud usando geopy (Nominatim).
@csrf_exempt
def agregar_playa(request):
    if request.method == 'POST':
        try:
            # Se extraen los datos del cuerpo de la petición
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            lugar = data.get('lugar', '').strip()

            # Validación: ambos campos son obligatorios
            if not nombre or not lugar:
                return JsonResponse({'ok': False, 'error': 'Faltan datos obligatorios.'})

            # Verificación: no permitir duplicados por nombre y lugar (ignorando mayúsculas)
            existe = Playa.objects.filter(
                nombre__iexact=nombre,
                lugar__iexact=lugar
            ).exists()

            if existe:
                return JsonResponse({'ok': False, 'error': 'Ya existe una playa con ese nombre y lugar.'})

            # Geolocaliza la playa combinando nombre y lugar
            geolocator = Nominatim(user_agent="app_playas")
            location = geolocator.geocode(f"{nombre}, {lugar}")

            if location:
                # Si encuentra coordenadas, crea la playa en la base de datos
                Playa.objects.create(
                    nombre=nombre,
                    lugar=lugar,
                    latitud=location.latitude,
                    longitud=location.longitude
                )
                return JsonResponse({'ok': True})
            else:
                return JsonResponse({'ok': False, 'error': 'No se pudo encontrar la ubicación.'})

        except Exception as e:
            # Manejo genérico de errores
            return JsonResponse({'ok': False, 'error': str(e)})

    # Rechaza métodos distintos de POST
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


# === Eliminar Playa ===
# Recibe un ID y elimina la playa correspondiente si existe.
@csrf_exempt
def eliminar_playa(request, playa_id):
    if request.method == 'DELETE':
        try:
            playa = Playa.objects.get(id=playa_id)
            playa.delete()
            return JsonResponse({'ok': True})
        except Playa.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Playa no encontrada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


# === Datos Actuales del API MARINE ===
# Llama al endpoint de Open-Meteo MARINE para obtener condiciones actuales del mar
def get_current_marine_data(lat, lon):
    url = (
        f"https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}&longitude={lon}"
        f"&current=wave_height,wave_direction,wave_period,"
        f"swell_wave_height,swell_wave_direction,swell_wave_period,sea_surface_temperature"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("current", {})
    return None


# === Datos Actuales del API WEATHER ===
# Llama al endpoint de Open-Meteo FORECAST para obtener condiciones meteorológicas actuales
def get_current_weather_data(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,weather_code"
        f"&timezone=Europe%2FBerlin&forecast_days=1"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("current", {})
    return None
