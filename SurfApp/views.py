from datetime import date, timedelta
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


def _diferencia_angular(a, b):
    """Devuelve la diferencia angular mínima (0..180°) entre dos direcciones."""
    diff = abs(float(a) - float(b)) % 360
    return 360 - diff if diff > 180 else diff


def _calcular_nivel_surf(current_marine, current_weather, playa=None):
    """Calcula una puntuación de 1 a 5 estrellas para 3 niveles teniendo en cuenta orientación óptima."""
    wave = (current_marine or {}).get("wave_height")
    period = (current_marine or {}).get("wave_period") or 0
    wave_dir = (current_marine or {}).get("wave_direction")
    wind = (current_weather or {}).get("wind_speed_10m")
    wind_dir = (current_weather or {}).get("wind_direction_10m")

    if wave is None:
        return [
            {"nivel": "Principiante", "stars": 0, "nota": "Sin datos"},
            {"nivel": "Progresión", "stars": 0, "nota": "Sin datos"},
            {"nivel": "Intermedio", "stars": 0, "nota": "Sin datos"},
        ]

    wind_val = wind if wind is not None else 15

    # Principiante (espumas / primeras olas)
    if 0.3 <= wave <= 1.2 and wind_val <= 20:
        s_beg, n_beg = 5, "Condiciones ideales"
    elif wave <= 1.4 and wind_val <= 25:
        s_beg, n_beg = 4, "Muy bueno para empezar"
    elif wave <= 1.7 and wind_val <= 30:
        s_beg, n_beg = 3, "Aceptable con precaución"
    elif wave > 2.0 and wind_val > 35:
        s_beg, n_beg = 1, "Mar grande y mucho viento"
    elif wave > 2.0:
        s_beg, n_beg = 1, "Demasiada fuerza de ola"
    elif wind_val > 35:
        s_beg, n_beg = 1, "Demasiado viento"
    elif wave < 0.3:
        s_beg, n_beg = 2, "Mar muy pequeño"
    else:
        s_beg, n_beg = 2, "Ola exigente" if wave > 1.7 else "Viento molesto"

    # Progresión (pasa la rompiente / primeras paredes)
    if 0.6 <= wave <= 1.6 and wind_val <= 25:
        s_prog, n_prog = 5, "Ideal para progresar"
    elif wave <= 1.9 and wind_val <= 30:
        s_prog, n_prog = 4, "Buenas olas"
    elif wave <= 2.2 and wind_val <= 36:
        s_prog, n_prog = 3, "Retador"
    elif wave > 2.2 and wind_val > 36:
        s_prog, n_prog = 2, "Olas grandes y viento fuerte"
    elif wave > 2.2:
        s_prog, n_prog = 2, "Demasiado tamaño"
    elif wind_val > 36:
        s_prog, n_prog = 2, "Mucho viento"
    else:
        s_prog, n_prog = 2, "Olas pequeñas"

    # Intermedio (olas con fuerza y giro)
    if 0.9 <= wave <= 2.5 and period >= 7 and wind_val <= 30:
        s_int, n_int = 5, "Muy buenas condiciones"
    elif 0.7 <= wave <= 2.9 and wind_val <= 38:
        s_int, n_int = 4, "Divertido y surfeable"
    elif 0.5 <= wave <= 3.3 and wind_val <= 44:
        s_int, n_int = 3, "Surfeable"
    elif wind_val > 44:
        s_int, n_int = 2, "Demasiado viento"
    elif wave > 3.3:
        s_int, n_int = 2, "Mar muy grande"
    else:
        s_int, n_int = 2, "Falta tamaño" if wave < 0.5 else "Periodo corto"

    # Ajuste por orientación óptima de la playa (olas y viento)
    penalizacion = 0
    motivo_orientacion = None
    if playa is not None:
        if playa.ola_optima is not None and wave_dir is not None:
            diff_ola = _diferencia_angular(wave_dir, playa.ola_optima)
            if diff_ola > 75:
                penalizacion += 1
                motivo_orientacion = "Dirección de ola desfavorable"
        if playa.viento_optimo is not None and wind_dir is not None:
            diff_viento = _diferencia_angular(wind_dir, playa.viento_optimo)
            if diff_viento > 90:
                penalizacion += 1
                motivo_orientacion = "Viento desfavorable" if not motivo_orientacion else "Ola y viento desfavorables"

    if penalizacion > 0:
        s_beg = max(1, s_beg - penalizacion)
        s_prog = max(1, s_prog - penalizacion)
        s_int = max(1, s_int - penalizacion)
        n_beg = motivo_orientacion
        n_prog = motivo_orientacion
        n_int = motivo_orientacion

    return [
        {"nivel": "Principiante", "stars": s_beg, "nota": n_beg},
        {"nivel": "Progresión", "stars": s_prog, "nota": n_prog},
        {"nivel": "Intermedio", "stars": s_int, "nota": n_int},
    ]


# Vista que muestra la información del API sobre la playa en forma de dashboard
def dashboard_playa_view(request, playa_id):
    if not request.user.is_authenticated and not request.session.get('guest_mode'):
        return redirect('login')
    playa = get_object_or_404(Playa, id=playa_id)
    hoy = date.today()

    dia_param = request.GET.get('dia')
    try:
        selected_date = date.fromisoformat(dia_param) if dia_param else hoy
    except ValueError:
        selected_date = hoy

    # Solo pide a Open-Meteo Marine los días que realmente faltan en Supabase
    fin_semana = hoy + timedelta(days=6)
    fechas_existentes = set(
        MarineDailyData.objects.filter(playa=playa, fecha__gte=hoy, fecha__lte=fin_semana)
        .values_list('fecha', flat=True)
    )
    fechas_objetivo = [hoy + timedelta(days=i) for i in range(7)]
    fechas_faltantes = [f for f in fechas_objetivo if f not in fechas_existentes]
    if fechas_faltantes:
        fetch_and_save_marine_data(playa, start_date=fechas_faltantes[0], end_date=fechas_faltantes[-1])

    marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=selected_date).first()
    marine_hourly = MarineHourlyData.objects.filter(playa=playa, timestamp__date=selected_date).order_by('timestamp')

    weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=selected_date).order_by('timestamp')
    if selected_date == hoy and not weather_hourly:
        fetch_and_save_weather_data(playa)
        weather_hourly = WeatherHourlyData.objects.filter(playa=playa, timestamp__date=selected_date).order_by('timestamp')

    dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    dias_disponibles = []
    for offset in range(7):
        d = hoy + timedelta(days=offset)
        if offset == 0:
            label = 'Hoy'
        elif offset == 1:
            label = 'Mañana'
        else:
            label = f"{dias_semana[d.weekday()]} {d.day}"
        dias_disponibles.append({
            'fecha_iso': d.isoformat(),
            'label': label,
            'activo': d == selected_date,
        })
    

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

    # Prepara los 7 días completos en JSON para cambiar de día al instante en el navegador
    week_daily = MarineDailyData.objects.filter(playa=playa, fecha__gte=hoy, fecha__lte=fin_semana)
    week_hourly = MarineHourlyData.objects.filter(
        playa=playa, timestamp__date__gte=hoy, timestamp__date__lte=fin_semana
    ).order_by('timestamp')

    daily_by_date = {
        d.fecha.isoformat(): {
            "wave_height_max": d.wave_height_max,
            "wave_direction_dominant": d.wave_direction_dominant,
            "wave_period_max": d.wave_period_max,
            "swell_wave_height_max": d.swell_wave_height_max,
            "swell_wave_direction_dominant": d.swell_wave_direction_dominant,
            "swell_wave_period_max": d.swell_wave_period_max,
            "levels": _calcular_nivel_surf(
                {
                    "wave_height": d.wave_height_max,
                    "wave_period": d.wave_period_max,
                    "wave_direction": d.wave_direction_dominant,
                },
                None,
                playa=playa,
            ),
        }
        for d in week_daily
    }
    hourly_by_date = {}
    for d in week_hourly:
        key = localtime(d.timestamp).date().isoformat()
        hourly_by_date.setdefault(key, []).append({
            "time": localtime(d.timestamp).strftime('%H:%M'),
            "wave_height": d.wave_height,
            "wave_period": d.wave_period,
            "wave_direction": d.wave_direction,
            "swell_wave_height": d.swell_wave_height,
            "swell_wave_period": d.swell_wave_period,
            "swell_wave_direction": d.swell_wave_direction,
        })
    week_data_json = json.dumps({"daily": daily_by_date, "hourly": hourly_by_date})

    context = {
        'playa': playa,
        'current_marine': current_marine,
        'current_weather': current_weather,
        'surf_levels': _calcular_nivel_surf(current_marine, current_weather, playa=playa),
        'day_surf_levels': (daily_by_date.get(selected_date.isoformat()) or {}).get(
            'levels',
            _calcular_nivel_surf(None, None),
        ),
        'marine_daily': marine_daily,
        'dias_disponibles': dias_disponibles,
        'selected_date': selected_date.isoformat(),
        'week_data_json': week_data_json,
        'weather_description': weather_description,
        'marine_hourly': list(marine_hourly),
        'weather_hourly': list(weather_hourly),
        'marine_hourly_json': marine_hourly_json,
        'weather_hourly_json': weather_hourly_json,
    }

    return render(request, 'dashboard.html', context)
