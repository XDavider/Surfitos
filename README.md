<h1 align="center"> Surfitos <br><br>
  
![github-header-image](https://github.com/user-attachments/assets/22561233-6b2d-496f-b368-38437b797b7b)


![Badge en Desarollo](https://img.shields.io/badge/Status-Ya%20desplegado!-yellow)
![Mantenido](https://img.shields.io/badge/Mantenido%3F-Si-green.svg)

![GitHub Org's stars](https://img.shields.io/github/stars/XDavider?style=social)

![Docker Badge](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff&style=flat)
![NGINX Badge](https://img.shields.io/badge/NGINX-009639?logo=nginx&logoColor=fff&style=flat)
![Django Badge](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=fff&style=flat)
![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=flat)
![JavaScript Badge](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=000&style=flat)
![HTML5 Badge](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=fff&style=flat)
![CSS3 Badge](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=fff&style=flat)
![SQLite Badge](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=fff&style=flat)
![PostgreSQL Badge](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=fff&style=flat)
![PyCharm Badge](https://img.shields.io/badge/PyCharm-000?logo=pycharm&logoColor=fff&style=flat)

</h1>

## 📚 Índice

- [🔍 Descripción del proyecto](#descripción-del-proyecto)
- [🚀 Funcionalidades principales](#funcionalidades-principales)
- [🧑‍💻 Tecnologías utilizadas](#tecnologías-utilizadas)
- [🛠️ Instalación y despliegue](#instalación-y-despliegue)
- [🌐 Uso de la API de Open-Meteo](#uso-de-la-api-de-open-meteo)
- [📸 Capturas de pantalla](#capturas-de-pantalla)
- [📦 Requisitos del sistema](#requisitos-del-sistema)

---

## 🔍 Descripción del proyecto

**Surfitos** es una aplicación web desarrollada como Trabajo de Fin de Grado. Su objetivo es permitir a los usuarios consultar en tiempo real las condiciones meteorológicas y del mar en diferentes playas agregadas por lo propios usuarios, con especial utilidad para surfistas y aficionados a deportes acuáticos.

La idea surge en el verano del 2024 cuando mis amigos y yo nos aficionamos al Surf después de probarlo por primera vez ese mismo verano, lo cual nos lleva a comprarnos tablas propias y equipamiento para dejar atrás las escuelas de surf y volvernos surfistas amateur, pero como principiantes que somos, nuestra lectura del tiempo y del mar aún le falta madurar, además, las paginas web hechas para sacar la información que necesitamos tienen publicidad, dan información demás, no concretan lo suficiente o no están hechas para surfistas, si no para marineros.

En ese momento propuse la idea de desarrollar una aplicación para nuestro uso privado centrada en el surf y nació Surfitos.

El proyecto ha sido desarrollado íntegramente por mí y está desplegado actualmente en:

[Surfitos](https://surfitos.mooo.com/)

---

## 🚀 Funcionalidades principales

- Login y autenticación de usuarios
- Selección y gestión de playas
- Visualización de información meteorológica y marítima
- Integración con mapas para localización de playas
- Dashboard con datos actuales y predicciones


---

## 🧑‍💻 Tecnologías utilizadas

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Django
- **API externa:** [Open-Meteo](https://open-meteo.com/)
- **Base de datos:** SQLite en desarrollo, Postgres en producción
- **Despliegue:** Docker, Nginx
- **Servidor:** Ubuntu 20.04 (equipo local con acceso SSH)

---

## 🛠️ Instalación y despliegue

### 🔧 Requisitos previos

Antes de comenzar, asegúrate de tener instalado:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Git](https://git-scm.com/)


### 📥 1. Clonar el repositorio

```bash
git clone https://github.com/XDavider/surfitos.git
cd Surfitos
```

### 🐳 2. Construir y levantar los contenedores

```bash
docker-compose up --build
```

### 🌍 3. Acceder a la aplicación

Una vez los contenedores estén corriendo, abre tu navegador en:

http://localhost:8000
<br>
<br>
#### 📌 Producción: uso de Nginx

Este proyecto incluye una configuración de Nginx dentro del contenedor para servir correctamente los archivos estáticos (CSS, JS, imágenes) y enrutar las peticiones al backend de Django.

> [!NOTE]
> 💡 Si planeas desplegar el proyecto en un servidor real (como en surfitos.mooo.com), es recomendable mantener el uso de Nginx u otro servidor proxy inverso similar (como Apache o Caddy) para:
>>- Servir contenido estático de forma eficiente
>> 
>>- Gestionar certificados SSL (HTTPS)
>> 
>>- Reenviar correctamente peticiones al backend (reverse proxy)
>> 
>>- Mejorar la seguridad general de la aplicación
<br>
<br>        
       
### ⚙️ 4. Comandos útiles

  Detener los contenedores:
    
  ```bash
  docker-compose down
  ```

  Reconstruir y reiniciar:
    
  ```bash
  docker-compose up --build
  ```
<br>


### 🐘 5. Migraciones y superusuario (opcional)

Dentro del contenedor, puedes ejecutar comandos Django como migraciones o crear un superusuario:

```bash
docker exec -it surfitos-backend bash
python manage.py migrate
python manage.py createsuperuser
```

---

## 🌐 Uso de la API de Open-Meteo

- **Current weather**: se consulta en tiempo real al cargar el dashboard.
- **Daily forecast**: datos como máximas/mínimas se almacenan cada día.
- **Hourly forecast**: datos por hora usados para gráficos de tendencias.

  
---

## 📸 Capturas de pantalla

- Login
  
  ![imagen](https://github.com/user-attachments/assets/7719b593-49b4-4586-9f56-6b9239027365)

- Lista de playas
  
  ![imagen](https://github.com/user-attachments/assets/4b2151e8-eae0-4483-a49c-14b9e94fff0a)

- Modo mapa
  
  ![imagen](https://github.com/user-attachments/assets/7854b61e-062d-4a69-adc9-5324368891b3)

- Dashboard
  
  - Header
    
  ![imagen](https://github.com/user-attachments/assets/86a5032d-c2fd-4ba3-a7e8-80892458819b)

  - Gráfica interactiva
    
  ![imagen](https://github.com/user-attachments/assets/cf8f703b-1c1b-4ca0-ae9e-51adce652887)

  - Tarjetas de datos
    
  ![imagen](https://github.com/user-attachments/assets/00404b1b-3373-442d-9ecc-0a8099acf4ed)

  - Mapa Interactivo
    
  ![imagen](https://github.com/user-attachments/assets/9086a089-264c-455f-8bfb-3b70fd6bdd4e)



---

## 📦 Requisitos del sistema

- **Sistema operativo:** Ubuntu 20.04+ recomendado
- **CPU:** 2 núcleos
- **RAM:** 2 GB mínimo
- **Disco:** 10 GB libres
- **Software:** Docker, Git
