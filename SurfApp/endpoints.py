import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from .models import Playa
import json

# Vista que permite agregar una nueva playa desde el frontend (POST con JSON)
@csrf_exempt
def agregar_playa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            lugar = data.get('lugar', '').strip()

            # Validación de campos obligatorios
            if not nombre or not lugar:
                return JsonResponse({'ok': False, 'error': 'Faltan datos obligatorios.'})

            # Verificación: evitar duplicados
            existe = Playa.objects.filter(
                nombre__iexact=nombre,
                lugar__iexact=lugar
            ).exists()

            if existe:
                return JsonResponse({'ok': False, 'error': 'Ya existe una playa con ese nombre y lugar.'})

            # Geolocaliza la playa usando Nominatim
            geolocator = Nominatim(user_agent="app_playas")
            location = geolocator.geocode(f"{nombre}, {lugar}")

            if location:
                # Si se encuentra la ubicación, se guarda en la base de datos
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
            # Si ocurre un error inesperado
            return JsonResponse({'ok': False, 'error': str(e)})

    # Si no es POST, devuelve error 405
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

# Vista para eliminar una playa según su ID (desde botón 🗑️)
@csrf_exempt
def eliminar_playa(request, playa_id):
    if request.method == 'DELETE':
        try:
            # Busca la playa por ID y la elimina
            playa = Playa.objects.get(id=playa_id)
            playa.delete()
            return JsonResponse({'ok': True})
        except Playa.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Playa no encontrada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    # Si no es DELETE, devuelve error 405
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

def get_current_marine_data(lat, lon):
    url = f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}&current=wave_height,wave_direction,wave_period,sea_surface_temperature"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("current", {})
    return None

def get_current_weather_data(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,apparent_temperature,weather_code&timezone=Europe%2FBerlin&forecast_days=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("current", {})
    return None
