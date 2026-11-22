import json
import time
import requests
from django.core.cache import cache
from django.http import JsonResponse
from geopy.geocoders import Nominatim
from .models import Playa

# === Agregar Playa ===
# Permite agregar una playa desde el frontend vía POST con JSON.
# Requiere nombre y lugar; se obtiene latitud y longitud usando geopy (Nominatim).
def agregar_playa(request):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Autenticación requerida.'}, status=401)

    if request.method == 'POST':
        try:
            # Se extraen los datos del cuerpo de la petición
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            lugar = data.get('lugar', '').strip() or 'Ubicación personalizada'
            latitud = data.get('latitud')
            longitud = data.get('longitud')

            if not nombre:
                return JsonResponse({'ok': False, 'error': 'El nombre es obligatorio.'})

            if len(nombre) > 100 or len(lugar) > 100:
                return JsonResponse(
                    {'ok': False, 'error': 'El nombre y el lugar no pueden superar los 100 caracteres.'},
                    status=400,
                )

            existe = Playa.objects.filter(
                nombre__iexact=nombre,
                lugar__iexact=lugar
            ).exists()

            if existe:
                return JsonResponse({'ok': False, 'error': 'Ya existe una playa con ese nombre y lugar.'})

            ola_optima = data.get('ola_optima')
            viento_optimo = data.get('viento_optimo')
            ola_optima = int(ola_optima) if ola_optima not in (None, '') else None
            viento_optimo = int(viento_optimo) if viento_optimo not in (None, '') else None

            if latitud is not None and longitud is not None:
                Playa.objects.create(
                    nombre=nombre,
                    lugar=lugar,
                    latitud=float(latitud),
                    longitud=float(longitud),
                    ola_optima=ola_optima,
                    viento_optimo=viento_optimo,
                )
                return JsonResponse({'ok': True})

            geolocator = Nominatim(user_agent="surfitos_app")
            location = geolocator.geocode(f"{nombre}, {lugar}", timeout=10)

            if location:
                Playa.objects.create(
                    nombre=nombre,
                    lugar=lugar,
                    latitud=location.latitude,
                    longitud=location.longitude
                )
                return JsonResponse({'ok': True})
            return JsonResponse({'ok': False, 'error': 'No se pudo encontrar la ubicación.'})

        except Exception as e:
            # Manejo genérico de errores
            return JsonResponse({'ok': False, 'error': str(e)})

    # Rechaza métodos distintos de POST
    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


# === Editar Playa ===
def editar_playa(request, playa_id):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Autenticación requerida.'}, status=401)

    if request.method == 'PUT':
        try:
            playa = Playa.objects.get(id=playa_id)
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            lugar = data.get('lugar', '').strip() or 'Ubicación personalizada'
            latitud = data.get('latitud')
            longitud = data.get('longitud')
            ola_optima = data.get('ola_optima')
            viento_optimo = data.get('viento_optimo')

            if not nombre:
                return JsonResponse({'ok': False, 'error': 'El nombre es obligatorio.'})
            if len(nombre) > 100 or len(lugar) > 100:
                return JsonResponse({'ok': False, 'error': 'Máximo 100 caracteres.'}, status=400)

            playa.nombre = nombre
            playa.lugar = lugar
            if latitud is not None and longitud is not None:
                playa.latitud = float(latitud)
                playa.longitud = float(longitud)
            playa.ola_optima = int(ola_optima) if ola_optima not in (None, '') else None
            playa.viento_optimo = int(viento_optimo) if viento_optimo not in (None, '') else None
            playa.save()
            return JsonResponse({'ok': True})
        except Playa.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Playa no encontrada'})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)})

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)


# === Eliminar Playa ===
# Recibe un ID y elimina la playa correspondiente si existe.
def eliminar_playa(request, playa_id):
    if not request.user.is_authenticated:
        return JsonResponse({'ok': False, 'error': 'Autenticación requerida.'}, status=401)

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
# Llama al endpoint de Open-Meteo MARINE con caché de 10 minutos para reducir llamadas
def get_current_marine_data(lat, lon):
    cache_key = f"current_marine_{round(float(lat), 4)}_{round(float(lon), 4)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = (
        f"https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}&longitude={lon}"
        f"&current=wave_height,wave_direction,wave_period,"
        f"swell_wave_height,swell_wave_direction,swell_wave_period,"
        f"wind_wave_height,wind_wave_period,sea_surface_temperature"
    )
    for attempt in range(2):
        try:
            response = requests.get(url, headers={"User-Agent": "SurfitosApp/1.0"}, timeout=10)
            if response.status_code == 200:
                data = response.json().get("current", {})
                if data:
                    cache.set(cache_key, data, 600)
                return data
            print(f"[Open-Meteo Current Marine] attempt={attempt+1} status={response.status_code}")
        except requests.RequestException as exc:
            print(f"[Open-Meteo Current Marine] attempt={attempt+1} error: {exc}")
        if attempt == 0:
            time.sleep(0.5)
    return None


# === Datos Actuales del API WEATHER ===
# Llama al endpoint de Open-Meteo FORECAST con caché de 10 minutos para reducir llamadas
def get_current_weather_data(lat, lon):
    cache_key = f"current_weather_{round(float(lat), 4)}_{round(float(lon), 4)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,weather_code,"
        f"wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation,cloud_cover"
        f"&timezone=Europe%2FBerlin&forecast_days=1"
    )
    for attempt in range(2):
        try:
            response = requests.get(url, headers={"User-Agent": "SurfitosApp/1.0"}, timeout=10)
            if response.status_code == 200:
                data = response.json().get("current", {})
                if data:
                    cache.set(cache_key, data, 600)
                return data
            print(f"[Open-Meteo Current Weather] attempt={attempt+1} status={response.status_code}")
        except requests.RequestException as exc:
            print(f"[Open-Meteo Current Weather] attempt={attempt+1} error: {exc}")
        if attempt == 0:
            time.sleep(0.5)

    # Fallback a api.met.no (Yr.no) si Open-Meteo Forecast bloquea/limita la IP de Vercel
    try:
        met_url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={round(float(lat), 4)}&lon={round(float(lon), 4)}"
        met_resp = requests.get(met_url, headers={"User-Agent": "SurfitosApp/1.0 github.com/XDavider/Surfitos"}, timeout=10)
        if met_resp.status_code == 200:
            ts = met_resp.json().get("properties", {}).get("timeseries", [])
            if ts:
                details = ts[0].get("data", {}).get("instant", {}).get("details", {})
                next_1h = ts[0].get("data", {}).get("next_1_hours", {}).get("details", {})
                wind_ms = details.get("wind_speed")
                data = {
                    "temperature_2m": details.get("air_temperature"),
                    "apparent_temperature": details.get("air_temperature"),
                    "wind_speed_10m": round(wind_ms * 3.6, 1) if wind_ms is not None else None,
                    "wind_direction_10m": details.get("wind_from_direction"),
                    "wind_gusts_10m": round(details.get("wind_speed_of_gust") * 3.6, 1) if details.get("wind_speed_of_gust") is not None else None,
                    "cloud_cover": details.get("cloud_area_fraction"),
                    "precipitation": next_1h.get("precipitation_amount", 0),
                    "weather_code": 3 if (details.get("cloud_area_fraction") or 0) > 70 else (2 if (details.get("cloud_area_fraction") or 0) > 30 else 0),
                }
                cache.set(cache_key, data, 600)
                return data
    except requests.RequestException as exc:
        print(f"[Met.no Current Weather] error: {exc}")
    return None
