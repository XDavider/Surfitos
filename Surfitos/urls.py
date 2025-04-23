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
from SurfApp import views

# Definición de las rutas del proyecto
urlpatterns = [
    # Ruta al panel de administración de Django
    path('admin/', admin.site.urls),

    # Página de inicio: muestra el login
    path('', views.login_view, name='login' ),

    # Vista principal que lista las playas (requiere login)
    path('playas/', views.playas_index_view, name='playas' ),

    # API para agregar una nueva playa vía POST
    path('api/agregar-playa/', views.agregar_playa, name='agregar_playa'),

    # API para eliminar una playa por ID vía DELETE
    path('api/eliminar-playa/<str:playa_id>', views.eliminar_playa, name='eliminar_playa'),

# Añade soporte para servir archivos estáticos durante el desarrollo
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
