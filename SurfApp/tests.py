import json
from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from SurfApp.models import MarineDailyData, MarineHourlyData, Playa, WeatherHourlyData
from SurfApp.views import _calcular_nivel_surf, _diferencia_angular

User = get_user_model()


class SurfitosUnitTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="surfer", password="secret")
        self.playa = Playa.objects.create(
            nombre="Mar de fora",
            lugar="Fisterra",
            latitud=42.90861,
            longitud=-9.27471,
            ola_optima=270,
            viento_optimo=90,
        )

    def test_diferencia_angular(self):
        self.assertEqual(_diferencia_angular(0, 350), 10)
        self.assertEqual(_diferencia_angular(270, 90), 180)
        self.assertEqual(_diferencia_angular(45, 45), 0)

    def test_nivel_surf_penaliza_orientacion_desfavorable(self):
        marine_good = {"wave_height": 1.0, "wave_period": 10, "wave_direction": 270}
        weather_good = {"wind_speed_10m": 15, "wind_direction_10m": 90}
        levels_good = _calcular_nivel_surf(marine_good, weather_good, playa=self.playa)
        self.assertEqual(levels_good[0]["stars"], 5)

        marine_bad = {"wave_height": 1.0, "wave_period": 10, "wave_direction": 90}
        weather_bad = {"wind_speed_10m": 15, "wind_direction_10m": 270}
        levels_bad = _calcular_nivel_surf(marine_bad, weather_bad, playa=self.playa)
        self.assertEqual(levels_bad[0]["stars"], 3)
        self.assertEqual(levels_bad[0]["nota"], "Ola y viento desfavorables")

    def test_guest_mode_read_only_and_api_blocked(self):
        resp = self.client.post(reverse("login"), {"action": "guest"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(self.client.get(reverse("playas")).status_code, 200)

        # Un invitado no puede crear, editar ni borrar playas
        r_add = self.client.post(
            reverse("agregar_playa"),
            data=json.dumps({"nombre": "Test", "latitud": 43.0, "longitud": -8.0}),
            content_type="application/json",
        )
        self.assertEqual(r_add.status_code, 401)

        r_edit = self.client.put(
            reverse("editar_playa", args=[self.playa.id]),
            data=json.dumps({"nombre": "Hack"}),
            content_type="application/json",
        )
        self.assertEqual(r_edit.status_code, 401)

        r_del = self.client.delete(reverse("eliminar_playa", args=[self.playa.id]))
        self.assertEqual(r_del.status_code, 401)
        self.assertTrue(Playa.objects.filter(id=self.playa.id).exists())

    def test_authenticated_crud_playa(self):
        self.client.login(username="surfer", password="secret")

        r_add = self.client.post(
            reverse("agregar_playa"),
            data=json.dumps({
                "nombre": "Playa de Razo",
                "lugar": "Carballo",
                "latitud": 43.29041,
                "longitud": -8.70621,
                "ola_optima": 315,
                "viento_optimo": 135,
            }),
            content_type="application/json",
        )
        self.assertEqual(r_add.status_code, 200)
        self.assertTrue(r_add.json()["ok"])
        razo = Playa.objects.get(nombre="Playa de Razo")
        self.assertEqual(razo.ola_optima, 315)
        self.assertEqual(razo.viento_optimo, 135)

        r_edit = self.client.put(
            reverse("editar_playa", args=[razo.id]),
            data=json.dumps({
                "nombre": "Razo",
                "lugar": "Carballo",
                "ola_optima": 270,
                "viento_optimo": 90,
            }),
            content_type="application/json",
        )
        self.assertEqual(r_edit.status_code, 200)
        razo.refresh_from_db()
        self.assertEqual(razo.nombre, "Razo")
        self.assertEqual(razo.ola_optima, 270)

        r_del = self.client.delete(reverse("eliminar_playa", args=[razo.id]))
        self.assertEqual(r_del.status_code, 200)
        self.assertFalse(Playa.objects.filter(id=razo.id).exists())

    @patch("SurfApp.views.get_current_weather_data", return_value={"temperature_2m": 15.0, "wind_speed_10m": 12.0, "wind_direction_10m": 90, "weather_code": 0})
    @patch("SurfApp.views.get_current_marine_data", return_value={"wave_height": 1.2, "wave_period": 10.0, "wave_direction": 270, "sea_surface_temperature": 16.0})
    def test_dashboard_renders_with_cached_week_data(self, _mock_marine, _mock_weather):
        hoy = date.today()
        for i in range(7):
            d = hoy + timedelta(days=i)
            MarineDailyData.objects.create(
                playa=self.playa,
                fecha=d,
                wave_height_max=1.5,
                wave_direction_dominant=270,
                wave_period_max=10.0,
            )
        MarineHourlyData.objects.create(
            playa=self.playa,
            timestamp=timezone.now(),
            wave_height=1.2,
            wave_period=10.0,
            wave_direction=270,
        )
        WeatherHourlyData.objects.create(
            playa=self.playa,
            timestamp=timezone.now(),
            temperature=15.0,
            apparent_temperature=14.0,
            weather_code=0,
        )

        self.client.login(username="surfer", password="secret")
        resp = self.client.get(reverse("dashboard_playa", args=[self.playa.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Mar de fora")
