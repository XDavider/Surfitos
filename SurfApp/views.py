from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy.geocoders import Nominatim
from .models import Playa
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
            messages.error(request, 'Usuario o contraseña incorrectos.') # Si falla, muestra mensaje de error

    # Si es GET o si falló el login, renderiza el formulario
    return render(request, 'login.html')

# Vista principal que muestra la lista de playas
@login_required
def playas_index_view(request):
    playas = Playa.objects.all().order_by('nombre') # Obtiene todas las playas ordenadas por nombre
    return render(request, 'playas-index.html', {'playas': playas}) # Renderiza plantilla con contexto


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