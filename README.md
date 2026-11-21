<div align="center">
  <img src="SurfApp/static/SurfApp/img/surfitos-logo.png" alt="Surfitos Logo" width="120" />
  <h1>Surfitos</h1>
  <p><strong>Previsión de olas, mar de fondo y viento para surfistas</strong></p>

  ![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=fff&style=flat)
  ![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=fff&style=flat)
  ![Vercel](https://img.shields.io/badge/Vercel-000000?logo=vercel&logoColor=fff&style=flat)
  ![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=fff&style=flat)
  ![Open-Meteo](https://img.shields.io/badge/Open--Meteo-Marine%20%26%20Weather-0EA5E9?style=flat)
</div>

---

## Descripción

**Surfitos** es una aplicación web desarrollada en **Django** nacida como Trabajo de Fin de Grado para consultar de forma rápida, limpia y sin publicidad las condiciones del mar y del tiempo en tus spots de surf favoritos.

* **En producción:** [surfitos.vercel.app](https://surfitos.vercel.app/)

---

## Funcionalidades principales

* **Autenticación y Modo Invitado (Solo Lectura):** Acceso privado con usuario/contraseña o entrada rápida como invitado para consultar playas sin poder crear ni eliminar spots.
* **Gestión de Playas mediante Mapa Interactivo:** Añade cualquier playa haciendo clic directamente en el mapa (**Leaflet + OpenStreetMap**) y asígnale un nombre personalizado, o elimínala con confirmación integrada.
* **Dashboard Orientado al Surf:**
  * **Valoración por Nivel (1 a 5 estrellas):** Puntuación automática para *Principiante*, *Progresión*, *Intermedio* y *Profesional* con el motivo exacto (fuerza de ola, viento, periodo o tamaño).
  * **Condiciones Actuales en Tabla:** Altura, periodo y dirección de olas y *swell*, velocidad/dirección del viento, temperatura del agua, precipitación y nubosidad.
  * **Previsión a 7 Días Instantánea:** Barra selectora de días que actualiza al instante la valoración por nivel, la gráfica horaria y los máximos diarios sin recargar la página.
  * **Gráfica Horaria Interactiva (Chart.js):** Series configurables con paleta oceánica.
  * **Mapa de Oleaje Embebido (Windy):** Visualización en tiempo real de olas sobre el spot.

---

## Arquitectura y Optimización

* **Backend:** Django 5 (`SurfApp`), servido en **Vercel** (`@vercel/python`, `WhiteNoise` para estáticos).
* **Base de datos:** **Supabase** (PostgreSQL 17 vía *Session Pooler* IPv4 con SSL).
* **APIs externas:**
  * **Open-Meteo Marine API** (oleaje, periodo, dirección, *swell*, temperatura del agua).
  * **Open-Meteo Forecast API** con *fallback* automático a **Met.no (Yr.no)** para viento, temperatura, lluvia y nubosidad.
* **Eficiencia de llamadas:**
  * Descarga incremental: solo solicita a Open-Meteo los días que faltan en Supabase dentro de la ventana de 7 días.
  * Caché de 10 minutos (`django.core.cache`) para las condiciones actuales.

---

## Desarrollo local

1. Clona el repositorio y crea un entorno virtual:
   ```bash
   git clone https://github.com/XDavider/Surfitos.git
   cd Surfitos
   python -m venv .venv
   pip install -r requirements.txt
   ```
2. Copia `.env.example` a `.env` (para SQLite local basta con `USE_POSTGRES=False` y `DEBUG=True`).
3. Ejecuta migraciones y levanta el servidor:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

---

## Autor

* **David Bermúdez (`XDavider`)**
* [GitHub](https://github.com/XDavider/Surfitos) · [LinkedIn](https://www.linkedin.com/in/david-bermudez-445785403/) · [Instagram](https://www.instagram.com/david_de_dora/)
