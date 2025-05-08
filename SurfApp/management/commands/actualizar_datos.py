from django.core.management.base import BaseCommand
from SurfApp.models import Playa
from SurfApp.api_data_fetch import fetch_and_save_marine_data, fetch_and_save_weather_data

class Command(BaseCommand):
    help = 'Actualiza los datos diarios y horarios de todas las playas desde Open-Meteo'

    def handle(self, *args, **kwargs):
        playas = Playa.objects.all()

        if not playas.exists():
            self.stdout.write(self.style.WARNING("No hay playas registradas en la base de datos."))
            return

        for playa in playas:
            self.stdout.write(f"\nActualizando datos para: {playa.nombre} ({playa.lugar})")
            try:
                fetch_and_save_marine_data(playa)
                self.stdout.write(self.style.SUCCESS("✓ Datos marinos actualizados"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al actualizar datos marinos: {str(e)}"))

            try:
                fetch_and_save_weather_data(playa)
                self.stdout.write(self.style.SUCCESS("✓ Datos meteorológicos actualizados"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error al actualizar datos meteorológicos: {str(e)}"))
