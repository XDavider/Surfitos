from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
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
    return render(request, 'dashboard.html',
                  {'playa': playa})  # Renderiza la plantilla 'dashboard.html' y le pasa el objeto 'playa' al contexto
