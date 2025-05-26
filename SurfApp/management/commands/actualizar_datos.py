from django.core.management.base import BaseCommand
from SurfApp.models import Playa
from SurfApp.api_data_fetch import fetch_and_save_marine_data, fetch_and_save_weather_data

# === Comando personalizado de Django para actualizar datos ===
# Ejecuta la actualización de datos marinos y meteorológicos desde Open-Meteo
# para todas las playas registradas en la base de datos.
class Command(BaseCommand):
    help = 'Actualiza los datos diarios y horarios de todas las playas desde Open-Meteo'

    # Método principal que se ejecuta al llamar a este comando: `python manage.py actualizar_datos`
    def handle(self, *args, **kwargs):
        playas = Playa.objects.all()  # Obtiene todas las playas registradas

        if not playas.exists():
            # Si no hay playas, muestra una advertencia y termina
            self.stdout.write(self.style.WARNING("No hay playas registradas en la base de datos."))
            return

        # Itera sobre cada playa y actualiza sus datos
        for playa in playas:
            self.stdout.write(f"\nActualizando datos para: {playa.nombre} ({playa.lugar})")

            # Intenta actualizar los datos marinos
            try:
                fetch_and_save_marine_data(playa)
                self.stdout.write(self.style.SUCCESS("✓ Datos marinos actualizados"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al actualizar datos marinos: {str(e)}"))

            # Intenta actualizar los datos meteorológicos
            try:
                fetch_and_save_weather_data(playa)
                self.stdout.write(self.style.SUCCESS("✓ Datos meteorológicos actualizados"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al actualizar datos meteorológicos: {str(e)}"))
