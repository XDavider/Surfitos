// Constantes para los datos de la gráfica
const weatherCodeMap = {
    0: "☀️ Despejado",
    1: "🌤️ Mayormente despejado",
    2: "⛅ Parcialmente nublado",
    3: "☁️ Nublado",
    45: "🌫️ Niebla",
    48: "🌫️ Niebla con escarcha",
    51: "🌦️ Llovizna ligera",
    53: "🌧️ Llovizna moderada",
    55: "🌧️ Llovizna intensa",
    56: "❄️🌧️ Llovizna helada ligera",
    57: "❄️🌧️ Llovizna helada intensa",
    61: "🌦️ Lluvia ligera",
    63: "🌧️ Lluvia moderada",
    65: "🌧️ Lluvia intensa",
    66: "🌧️❄️ Lluvia helada ligera",
    67: "🌧️❄️ Lluvia helada intensa",
    71: "🌨️ Nieve ligera",
    73: "🌨️ Nieve moderada",
    75: "🌨️ Nieve intensa",
    77: "❄️ Granos de nieve",
    80: "🌦️ Chubascos ligeros",
    81: "🌧️ Chubascos moderados",
    82: "🌧️🌩️ Chubascos fuertes",
    85: "🌨️ Chubascos de nieve ligeros",
    86: "🌨️ Chubascos de nieve intensos",
    95: "⛈️ Tormenta eléctrica",
    96: "⛈️ Tormenta con granizo ligero",
    99: "⛈️ Tormenta con granizo fuerte"
};

// Ejecuta este bloque cuando el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", function () {
    // Obtiene el div oculto con los atributos data-lat y data-lon
    const coordDiv = document.getElementById("coord");
    const lat = parseFloat(coordDiv.dataset.lat);
    const lon = parseFloat(coordDiv.dataset.lon);

    // Inicializa el mapa de Leaflet en el div con id "mapa-playa"
    const map = L.map('mapa-playa', {
        center: [lat, lon],     // Centra el mapa en las coordenadas de la playa
        zoom: 15,               // Zoom inicial (puede ajustarse según preferencia)
        zoomControl: false,     // Oculta los botones de zoom (+/-)
        dragging: false,        // Desactiva el arrastre del mapa
        scrollWheelZoom: false,  // Permite hacer zoom con la rueda del ratón
        doubleClickZoom: false, // Desactiva el zoom por doble clic
        boxZoom: false,         // Desactiva zoom por selección con caja
        keyboard: false,        // Desactiva navegación con teclado
        touchZoom: true        // Desactiva zoom con gestos táctiles
    });

    // Añade la capa de mapas de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '',        // No muestra atribución (podés agregarla si querés)
        maxZoom: 28             // Máximo nivel de zoom permitido
    }).addTo(map);

    // Coloca un marcador en las coordenadas de la playa
    L.marker([lat, lon]).addTo(map);

    // Corrige un problema visual: obliga a Leaflet a recalcular el tamaño del mapa
    setTimeout(() => {
        map.invalidateSize({pan: false});
    }, 300);
});

// Función para mostrar la hora y fecha actual en el dashboard
function actualizarHora() {
    const ahora = new Date();

    // Formatea la fecha en formato largo (día, mes, año)
    const opciones = {year: 'numeric', month: 'long', day: 'numeric'};
    const fecha = ahora.toLocaleDateString('es-ES', opciones);

    // Formatea la hora con dos dígitos (ej. 14:05)
    const hora = ahora.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});

    // Inserta el resultado en el elemento con id "hora-actual"
    document.getElementById('hora-actual').textContent = `${fecha} - ${hora}`;
}

// Ejecuta la función de hora una vez que el DOM esté listo
document.addEventListener("DOMContentLoaded", actualizarHora);

// Espera a que el contenido del DOM esté cargado antes de ejecutar
document.addEventListener("DOMContentLoaded", () => {

    // Obtiene los datos horarios de variables marinas y meteorológicas desde el HTML (inyectados como JSON desde Django)
    const marineData = JSON.parse(document.getElementById("marine-data").textContent);
    const weatherData = JSON.parse(document.getElementById("weather-data").textContent);

    // Obtiene el contexto del lienzo (canvas) donde se renderiza la gráfica
    const ctx = document.getElementById("grafico-hourly").getContext("2d");

    // Crea las etiquetas del eje X a partir de las horas (formato HH:MM)
    const labels = marineData.map(d => d.time);  // Asume que todas las variables comparten el mismo eje temporal

    // Define los datasets para la gráfica, uno por variable (cada uno con su color y estado inicial visible/oculto)
    const datasets = {
        wave_height: {
            label: "Altura de ola (m)",
            data: marineData.map(d => d.wave_height),
            borderColor: "rgba(100, 100, 255, 1)",
            yAxisID: 'y_altura',
            hidden: false
        },
        wave_period: {
            label: "Periodo de ola (s)",
            data: marineData.map(d => d.wave_period),
            borderColor: "rgba(30, 0, 255, 1)",
            yAxisID: 'y_periodo',
            hidden: true
        },
        wave_direction: {
            label: "Dirección de las olas (º)",
            data: marineData.map(d => d.wave_direction),
            borderColor: "rgba(75, 192, 192, 1)",
            yAxisID: 'y_direccion',
            hidden: true
        },
        swell_wave_height: {
            label: "Altura del Mar de fondo (m)",
            data: marineData.map(d => d.swell_wave_height),
            borderColor: "rgba(255, 150, 200, 1)",
            yAxisID: 'y_altura',
            hidden: false
        },
        swell_wave_period: {
            label: "Periodo del Mar de fondo (s)",
            data: marineData.map(d => d.swell_wave_period),
            borderColor: "rgba(210, 70, 180, 1)",
            yAxisID: 'y_periodo',
            hidden: true
        },
        swell_wave_direction: {
            label: "Dirección del Mar de fondo (º)",
            data: marineData.map(d => d.swell_wave_direction),
            borderColor: "rgba(200, 50, 255, 1)",
            yAxisID: 'y_direccion',
            hidden: true
        },
        temperature: {
            label: "Temperatura (ºC)",
            data: weatherData.map(d => d.temperature),
            borderColor: "rgba(255, 0, 0, 1)",
            yAxisID: 'y_temp',
            hidden: true
        },
        apparent_temperature: {
            label: "Sensación térmica (ºC)",
            data: weatherData.map(d => d.apparent_temperature),
            borderColor: "rgba(255, 159, 64, 1)",
            yAxisID: 'y_temp',
            hidden: true
        },
        weather_code: {
            label: "Clima",
            data: weatherData.map(d => d.weather_code),
            borderColor: "rgba(240, 255, 0, 1)",
            yAxisID: 'y_codigo',
            hidden: true
        }
    };

    // Inicializa la gráfica usando Chart.js
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: labels,
        datasets: [
            {
                label: "Altura de ola (m)",
                data: marineData.map(d => d.wave_height),
                borderColor: "rgba(100, 100, 255, 1)",
                yAxisID: 'y_altura',
                hidden: false
            },
            {
                label: "Periodo de ola (s)",
                data: marineData.map(d => d.wave_period),
                borderColor: "rgba(30, 0, 255, 1)",
                yAxisID: 'y_periodo',
                hidden: true
            },
            {
                label: "Dirección de las olas (º)",
                data: marineData.map(d => d.wave_direction),
                borderColor: "rgba(75, 192, 192, 1)",
                yAxisID: 'y_direccion',
                hidden: true
            },
            {
                label: "Altura del Mar de fondo (m)",
                data: marineData.map(d => d.swell_wave_height),
                borderColor: "rgba(255, 150, 200, 1)",
                yAxisID: 'y_altura',
                hidden: false
            },
            {
                label: "Periodo del Mar de fondo (s)",
                data: marineData.map(d => d.swell_wave_period),
                borderColor: "rgba(210, 70, 180, 1)",
                yAxisID: 'y_periodo',
                hidden: true
            },
            {
                label: "Dirección del Mar de fondo (º)",
                data: marineData.map(d => d.swell_wave_direction),
                borderColor: "rgba(200, 50, 255, 1)",
                yAxisID: 'y_direccion',
                hidden: true
            },
            {
                label: "Temperatura (ºC)",
                data: weatherData.map(d => d.temperature),
                borderColor: "rgba(255, 0, 0, 1)",
                yAxisID: 'y_temp',
                hidden: true
            },
            {
                label: "Sensación térmica (ºC)",
                data: weatherData.map(d => d.apparent_temperature),
                borderColor: "rgba(255, 159, 64, 1)",
                yAxisID: 'y_temp',
                hidden: true
            },
            {
                label: "Clima",
                data: weatherData.map(d => d.weather_code),
                borderColor: "rgba(240, 255, 0, 1)",
                yAxisID: 'y_codigo',
                hidden: true
            }
        ]
    },
        options: {
        responsive: true,
        scales: {
            y_altura: {
                type: 'linear',
                position: 'right',
                title: { display: true, text: 'Altura (m)' },
                beginAtZero: true
            },
            y_periodo: {
                type: 'linear',
                position: 'right',
                title: { display: true, text: 'Periodo (s)' },
                grid: { drawOnChartArea: false }
            },
            y_direccion: {
                type: 'linear',
                position: 'right',
                offset: true,
                title: { display: true, text: 'Dirección (º)' },
                grid: { drawOnChartArea: false }
            },
            y_temp: {
                type: 'linear',
                position: 'left',
                offset: true,
                title: { display: true, text: 'Temperatura (°C)' },
                grid: { drawOnChartArea: false }
            },
            y_codigo: {
                type: 'linear',
                position: 'left',
                display: false
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const datasetLabel = context.dataset.label || '';
                        const value = context.raw;
                        if (datasetLabel.includes("Clima")) {
                            return `${datasetLabel}: ${weatherCodeMap[value] || 'N/D'}`;
                        }
                        return `${datasetLabel}: ${value}`;
                    }
                }
            }
        }
    }
});

    // 🔁 Asocia cada checkbox con su respectivo dataset
    document.querySelectorAll(".filtros input[type='checkbox']").forEach((checkbox, i) => {
        checkbox.addEventListener("change", () => {
            const key = Object.keys(datasets)[i];
            const dataset = chart.data.datasets.find(ds => ds.label === datasets[key].label);
            if (dataset) {
                dataset.hidden = !checkbox.checked; // Oculta o muestra según el checkbox
                chart.update(); // Actualiza la gráfica
            }
        });
    });
})
    ;