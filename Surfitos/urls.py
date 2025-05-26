"""
URL configuration for Surfitos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.views.static import serve 
from SurfApp import views
from SurfApp import endpoints  # ← nuevo

# Definición de las rutas del proyecto
urlpatterns = [

    path('', lambda request: redirect('playas')),

    # Ruta al panel de administración de Django
    path('admin/', admin.site.urls),

    # Página de inicio: muestra el login
    path('login/', views.login_view, name='login' ),

    # Vista principal que lista las playas (requiere login)
    path('playas/', views.playas_index_view, name='playas' ),

    # Vista que muestra la información de la playa seleccionada
    path('dashboard/<int:playa_id>/', views.dashboard_playa_view, name='dashboard_playa'),


    # API

    # API para agregar una nueva playa vía POST
    path('api/agregar-playa/', endpoints.agregar_playa, name='agregar_playa'),

    # API para eliminar una playa por ID vía DELETE
    path('api/eliminar-playa/<str:playa_id>', endpoints.eliminar_playa, name='eliminar_playa'),

    path('staticfiles/', serve,{'document_root': settings.STATIC_ROOT})

# Añade soporte para servir archivos estáticos durante el desarrollo
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

