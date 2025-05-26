from datetime import date
from django.utils.timezone import localtime
from SurfApp.models import MarineDailyData, WeatherDailyData, WeatherHourlyData, MarineHourlyData
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Playa
from .endpoints import get_current_marine_data, get_current_weather_data
from .api_data_fetch import (
    fetch_and_save_marine_data,
    fetch_and_save_weather_data,

)
from SurfApp.utils import decode_weather_code
import json


# Vista para el login del usuario
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Autenticación del usuario con el modelo User predeterminado
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Inicia sesión al usuario
            return redirect('playas')  # Redirige a la página principal o a alguna vista protegida
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')  # Si falla, muestra mensaje de error

    # Si es GET o si falló el login, renderiza el formulario
    return render(request, 'login.html')


# Vista principal que muestra la lista de playas
@login_required
def playas_index_view(request):
    playas = Playa.objects.all().order_by('nombre')  # Obtiene todas las playas ordenadas por nombre
    return render(request, 'playas-index.html', {'playas': playas})  # Renderiza plantilla con contexto


# Vista que muestra la información del API sobre la playa en forma de dashboard
@login_required
def dashboard_playa_view(request, playa_id):
    playa = Playa.objects.get(id=playa_id)  # Obtiene la instancia de la playa correspondiente al ID recibido por la URL
    hoy = date.today()

    # Datos diarios
    marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=hoy).first()
    weather_daily = WeatherDailyData.objects.filter(playa=playa, fecha=hoy).first()

    # Datos horarios de hoy
    marine_hourly = MarineHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
    weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
  
    # Si no hay datos, los obtiene de la API
    if not marine_daily or not weather_daily or not marine_hourly or not weather_hourly:
        fetch_and_save_marine_data(playa)
        fetch_and_save_weather_data(playa)
        marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=hoy).first()
        weather_daily = WeatherDailyData.objects.filter(playa=playa, fecha=hoy).first()
        marine_hourly = MarineHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
        weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=date.today()).order_by('timestamp')
    

    # Datos actuales
    current_marine = get_current_marine_data(playa.latitud, playa.longitud)
    current_weather = get_current_weather_data(playa.latitud, playa.longitud)
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
        'marine_daily': marine_daily,
        'weather_daily': weather_daily,
        'weather_description': weather_description,
        'marine_hourly': list(marine_hourly),
        'weather_hourly': list(weather_hourly),
        'marine_hourly_json': marine_hourly_json,
        'weather_hourly_json': weather_hourly_json,
    }

    return render(request, 'dashboard.html', context)
