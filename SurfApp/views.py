from datetime import date
from SurfApp.models import MarineDailyData, WeatherDailyData
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Playa
from .endpoints import get_current_marine_data, get_current_weather_data
from SurfApp.utils import decode_weather_code


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

    # Datos actuales
    current_marine = get_current_marine_data(playa.latitud, playa.longitud)
    current_weather = get_current_weather_data(playa.latitud, playa.longitud)
    weather_description = decode_weather_code(current_weather.get("weather_code")) if current_weather else "N/D"

    # Nuevos datos diarios
    marine_daily = MarineDailyData.objects.filter(playa=playa, fecha=hoy).first()
    weather_daily = WeatherDailyData.objects.filter(playa=playa, fecha=hoy).first()

    context = {
        'playa': playa,
        'current_marine': current_marine,
        'current_weather': current_weather,
        'marine_daily': marine_daily,
        'weather_daily': weather_daily,
        'weather_description': weather_description,
    }

    return render(request, 'dashboard.html', context)
