from datetime import date
from django.utils.timezone import localtime
from SurfApp.models import MarineDailyData, WeatherDailyData, WeatherHourlyData, MarineHourlyData
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Playa
from .endpoints import get_current_marine_data, get_current_weather_data
from .api_data_fetch import (
    fetch_and_save_marine_data,
    fetch_and_save_weather_data,

)
from SurfApp.utils import decode_weather_code
import json


# Vista para el login del usuario (y acceso como invitado en modo solo lectura)
def login_view(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'guest':
            logout(request)
            request.session['guest_mode'] = True
            return redirect('playas')

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        # Autenticación del usuario con el modelo User predeterminado
        user = authenticate(request, username=username, password=password)

        if user is not None:
            request.session.pop('guest_mode', None)
            login(request, user)  # Inicia sesión al usuario
            return redirect('playas')  # Redirige a la página principal o a alguna vista protegida
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')  # Si falla, muestra mensaje de error

    # Si es GET o si falló el login, renderiza el formulario
    return render(request, 'login.html')


def logout_view(request):
    request.session.pop('guest_mode', None)
    logout(request)
    return redirect('login')


# Vista principal que muestra la lista de playas (autenticado o invitado)
def playas_index_view(request):
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('login')
    playas = Playa.objects.all().order_by('nombre')  # Obtiene todas las playas ordenadas por nombre
    is_guest = not request.user.is_authenticated
    return render(request, 'playas-index.html', {'playas': playas, 'is_guest': is_guest})


def _calcular_nivel_surf(current_marine, current_weather):
    """Calcula una puntuación de 1 a 5 estrellas por nivel según olas, periodo y viento."""
    wave = (current_marine or {}).get("wave_height")
    period = (current_marine or {}).get("wave_period") or 0
    wind = (current_weather or {}).get("wind_speed_10m")

    if wave is None:
        return [
            {"nivel": "Principiante", "stars": 0, "nota": "Sin datos"},
            {"nivel": "Intermedio", "stars": 0, "nota": "Sin datos"},
            {"nivel": "Profesional", "stars": 0, "nota": "Sin datos"},
        ]

    wind_val = wind if wind is not None else 15

    # Principiante: olas suaves (0.4 - 1.3 m) y poco viento
    if 0.4 <= wave <= 1.2 and wind_val <= 18:
        s_beg, n_beg = 5, "Condiciones ideales"
    elif wave <= 1.6 and wind_val <= 25:
        s_beg, n_beg = 3, "Aceptable con precaución"
    elif wave > 2.0 or wind_val > 35:
        s_beg, n_beg = 1, "Demasiado fuerte"
    else:
        s_beg, n_beg = 2, "Algo exigente"

    # Intermedio: olas medianas (0.9 - 2.3 m), buen periodo
    if 0.9 <= wave <= 2.3 and period >= 8 and wind_val <= 25:
        s_int, n_int = 5, "Muy buenas condiciones"
    elif 0.6 <= wave <= 2.8 and wind_val <= 35:
        s_int, n_int = 3, "Surfeable"
    else:
        s_int, n_int = 2, "Condiciones difíciles"

    # Profesional: tamaño (>= 1.6 m) y periodo largo
    if wave >= 1.8 and period >= 9 and wind_val <= 35:
        s_pro, n_pro = 5, "Potente y limpio"
    elif wave >= 1.2 and wind_val <= 45:
        s_pro, n_pro = 3, "Divertido"
    else:
        s_pro, n_pro = 2, "Pequeño o muy pasado"

    return [
        {"nivel": "Principiante", "stars": s_beg, "nota": n_beg},
        {"nivel": "Intermedio", "stars": s_int, "nota": n_int},
        {"nivel": "Profesional", "stars": s_pro, "nota": n_pro},
    ]


# Vista que muestra la información del API sobre la playa en forma de dashboard
def dashboard_playa_view(request, playa_id):
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('login')
    playa = get_object_or_404(Playa, id=playa_id)  # Obtiene la instancia de la playa correspondiente al ID recibido por la URL
    hoy = date.today()

    # Datos diarios
    marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=hoy).first()
    weather_daily = WeatherDailyData.objects.filter(playa=playa, fecha=hoy).first()

    # Datos horarios de hoy
    marine_hourly = MarineHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
    weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
  
    # Si faltan datos marinos o meteorológicos, los obtiene de la API por separado
    if not marine_daily or not marine_hourly:
        fetch_and_save_marine_data(playa)
        marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=hoy).first()
        marine_hourly = MarineHourlyData.objects.filter(playa=playa, timestamp__date=hoy).order_by('timestamp')

    if not weather_daily or not weather_hourly:
        fetch_and_save_weather_data(playa)
        weather_daily = WeatherDailyData.objects.filter(playa=playa, fecha=hoy).first()
        weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=hoy).order_by('timestamp')
    

    # Datos actuales
    current_marine = get_current_marine_data(playa.latitud, playa.longitud)
    current_weather = get_current_weather_data(playa.latitud, playa.longitud)
    if not current_weather and weather_hourly.exists():
        current_hour = localtime().hour
        fallback = min(weather_hourly, key=lambda d: abs(localtime(d.timestamp).hour - current_hour))
        current_weather = {
            "temperature_2m": fallback.temperature,
            "apparent_temperature": fallback.apparent_temperature,
            "weather_code": fallback.weather_code,
        }
    weather_description = decode_weather_code(current_weather.get("weather_code")) if current_weather else "N/D"

    # Formatea los datos para el frontend
    marine_hourly_json = json.dumps([
        {
            "time": localtime(d.timestamp).strftime('%H:%M'),
            "wave_height": d.wave_height,
            "wave_period": d.wave_period,
            "wave_direction": d.wave_direction,
            "swell_wave_height": d.swell_wave_height,
            "swell_wave_period": d.swell_wave_period,
            "swell_wave_direction": d.swell_wave_direction,
        }
        for d in marine_hourly
    ])

    weather_hourly_json = json.dumps([
        {
            "time": localtime(d.timestamp).strftime('%H:%M'),
            "temperature": d.temperature,
            "apparent_temperature": d.apparent_temperature,
            "weather_code": d.weather_code,
        }
        for d in weather_hourly
    ])

    context = {
        'playa': playa,
        'current_marine': current_marine,
        'current_weather': current_weather,
        'surf_levels': _calcular_nivel_surf(current_marine, current_weather),
        'marine_daily': marine_daily,
        'weather_daily': weather_daily,
        'weather_description': weather_description,
        'marine_hourly': list(marine_hourly),
        'weather_hourly': list(weather_hourly),
        'marine_hourly_json': marine_hourly_json,
        'weather_hourly_json': weather_hourly_json,
    }

    return render(request, 'dashboard.html', context)
