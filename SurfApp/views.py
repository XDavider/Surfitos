from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from .models import Playa
import json


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
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')

@login_required
def playas_index_view(request):
    playas = Playa.objects.all().order_by('nombre')
    return render(request, 'playas-index.html', {'playas': playas})



@csrf_exempt
def agregar_playa(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            lugar = data.get('lugar', '').strip()

            if not nombre or not lugar:
                return JsonResponse({'ok': False, 'error': 'Faltan datos obligatorios.'})

            # Verificación: evitar duplicados
            existe = Playa.objects.filter(
                nombre__iexact=nombre,
                lugar__iexact=lugar
            ).exists()

            if existe:
                return JsonResponse({'ok': False, 'error': 'Ya existe una playa con ese nombre y lugar.'})

            # Buscar coordenadas
            geolocator = Nominatim(user_agent="app_playas")
            location = geolocator.geocode(f"{nombre}, {lugar}")

            if location:
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
            return JsonResponse({'ok': False, 'error': str(e)})

    return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
