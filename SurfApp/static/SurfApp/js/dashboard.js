// Constantes y funciones auxiliares
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

// Formatea el tiempo en un formato legible
function formatTime(timeString) {
    // Si el timeString ya está en formato HH:MM, devuélvelo tal cual
    if (/^\d{1,2}:\d{2}$/.test(timeString)) {
        return timeString;
    }
    
    // Si no, intenta analizarlo como fecha
    const date = new Date(timeString);
    if (date.toString() === 'Invalid Date') {        return timeString; // Devuelve el original si falla el análisis
    }
    
    return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
}

// Formatea la fecha
function formatDate(timeString) {
    const date = new Date(timeString);
    return date.toLocaleDateString('es-ES', { weekday: 'short', day: 'numeric', month: 'short' });
}

// Inicialización principal cuando el DOM está cargado
document.addEventListener("DOMContentLoaded", function () {
    initializeMap();
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000); // Actualiza el tiempo cada minuto
    initializeCharts();
});

// Inicializa el mapa
function initializeMap() {
    const coordDiv = document.getElementById("coord");
    const lat = parseFloat(coordDiv.dataset.lat);
    const lon = parseFloat(coordDiv.dataset.lon);

    const map = L.map('mapa-playa', {
        center: [lat, lon],
        zoom: 14,
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: false,
        doubleClickZoom: false,
        boxZoom: false,
        keyboard: false,
        touchZoom: false
    });    // Usa mosaicos de OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Añade un marcador personalizado
    const markerIcon = L.divIcon({
        className: 'custom-marker',
        html: '<i class="fas fa-map-marker-alt" style="color: #ec6ead; font-size: 24px; text-shadow: 0 0 5px rgba(0,0,0,0.5);"></i>',
        iconSize: [24, 24],
        iconAnchor: [12, 24]
    });

    L.marker([lat, lon], { icon: markerIcon }).addTo(map);    // Corrige problemas de visualización del mapa
    setTimeout(() => {
        map.invalidateSize();
    }, 300);
}

// Mantiene actualizada la hora actual
function updateCurrentTime() {
    const now = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const dateStr = now.toLocaleDateString('es-ES', options);
    const timeStr = now.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    document.getElementById('hora-actual').innerHTML = `<i class="far fa-clock"></i> ${dateStr} - ${timeStr}`;
}

// Inicializa las gráficas
function initializeCharts() {
    const marineData = JSON.parse(document.getElementById("marine-data").textContent);
    const weatherData = JSON.parse(document.getElementById("weather-data").textContent);

    const ctx = document.getElementById("grafico-hourly").getContext("2d");
    const labels = marineData.map(d => formatTime(d.time));
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: "#fff",
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: "rgba(0, 0, 0, 0.8)",
                    titleFont: {
                        family: "'Poppins', sans-serif",
                        size: 14
                    },
                    bodyFont: {
                        family: "'Poppins', sans-serif",
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const dataType = context.dataset.dataType;
                            if (dataType === 'weather-code') {
                                return weatherCodeMap[value] || 'N/D';
                            }
                            return `${context.dataset.label}: ${value}`;
                        }
                    }
                }
            },
            scales: {
                y_altura: {
                    type: 'linear',
                    position: 'right',
                    title: { 
                        display: true, 
                        text: 'Altura (m)',
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        }
                    },
                    beginAtZero: true,
                    grid: {
                        color: "rgba(255, 255, 255, 0.1)"
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.8)",
                        font: {
                            family: "'Poppins', sans-serif"
                        }
                    }
                },
                y_periodo: {
                    type: 'linear',
                    position: 'right',
                    title: { 
                        display: true, 
                        text: 'Periodo (s)',
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        }
                    },
                    grid: { 
                        drawOnChartArea: false,
                        color: "rgba(255, 255, 255, 0.1)"
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.8)",
                        font: {
                            family: "'Poppins', sans-serif"
                        }
                    }
                },
                y_direccion: {
                    type: 'linear',
                    position: 'right',
                    offset: true,
                    title: { 
                        display: true, 
                        text: 'Dirección (°)',
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        }
                    },
                    min: 0,
                    max: 360,
                    grid: { 
                        drawOnChartArea: false,
                        color: "rgba(255, 255, 255, 0.1)"
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.8)",
                        font: {
                            family: "'Poppins', sans-serif"
                        },
                        stepSize: 90,
                        callback: function(value) {
                            const directions = {
                                0: 'N',
                                90: 'E',
                                180: 'S',
                                270: 'O',
                                360: 'N'
                            };
                            return directions[value] || value;
                        }
                    }
                },
                y_temp: {
                    type: 'linear',
                    position: 'left',
                    offset: true,
                    title: { 
                        display: true, 
                        text: 'Temperatura (°C)',
                        color: 'rgba(255, 255, 255, 0.8)',
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 12
                        }
                    },
                    grid: { 
                        drawOnChartArea: false,
                        color: "rgba(255, 255, 255, 0.1)"
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.8)",
                        font: {
                            family: "'Poppins', sans-serif"
                        }
                    }
                },
                y_codigo: {
                    type: 'linear',
                    position: 'left',
                    display: false,
                    ticks: {
                        display: false
                    }
                },
                x: {
                    grid: {
                        color: "rgba(255, 255, 255, 0.1)"
                    },
                    ticks: {
                        color: "rgba(255, 255, 255, 0.8)",
                        font: {
                            family: "'Poppins', sans-serif",
                            size: 11
                        },
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            },            animation: {
                duration: 750,
                easing: 'easeInOutQuart',
                responsive: true,
                animateScale: true,
                animateRotate: true,
                animations: {
                    y: {
                        easing: 'easeInOutQuart',
                        from: (ctx) => {
                            if (ctx.type === 'data') {
                                if (ctx.mode === 'default' && !ctx.dropped) {
                                    ctx.dropped = true;
                                    return 0;
                                }
                            }
                            return ctx.chart.scales[ctx.scale.id].getPixelForValue(100);
                        }
                    }
                }
            }
        }
    });

    window.chartConfig = {
        chart: chart,
        marineData: marineData,
        weatherData: weatherData,
        datasetConfigs: {
            'wave': {
                label: "Altura de ola (m)",
                data: marineData.map(d => d.wave_height),
                borderColor: "#89CFF0", // Azul claro
                backgroundColor: "rgba(137, 207, 240, 0.2)",
                dataType: 'wave',
                yAxisID: 'y_altura'
            },
            'wave-period': {
                label: "Periodo de olas (s)",
                data: marineData.map(d => d.wave_period),
                borderColor: "#3494E6", // Azul medio
                backgroundColor: "rgba(52, 148, 230, 0.2)",
                dataType: 'wave-period',
                yAxisID: 'y_periodo'
            },
            'wave-direction': {
                label: "Dirección de olas (°)",
                data: marineData.map(d => d.wave_direction),
                borderColor: "#1B4B82", // Azul oscuro
                backgroundColor: "rgba(27, 75, 130, 0.2)",
                dataType: 'wave-direction',
                yAxisID: 'y_direccion'
            },
            'swell': {
                label: "Altura del Mar de fondo (m)",
                data: marineData.map(d => d.swell_wave_height),
                borderColor: "#FFB6C1", // Rosa claro
                backgroundColor: "rgba(255, 182, 193, 0.2)",
                dataType: 'swell',
                yAxisID: 'y_altura'
            },
            'swell-period': {
                label: "Periodo del Mar de fondo (s)",
                data: marineData.map(d => d.swell_wave_period),
                borderColor: "#FF69B4", // Rosa medio
                backgroundColor: "rgba(255, 105, 180, 0.2)",
                dataType: 'swell-period',
                yAxisID: 'y_periodo'
            },
            'swell-direction': {
                label: "Dirección del Mar de fondo (°)",
                data: marineData.map(d => d.swell_wave_direction),
                borderColor: "#C71585", // Rosa oscuro
                backgroundColor: "rgba(199, 21, 133, 0.2)",
                dataType: 'swell-direction',
                yAxisID: 'y_direccion'
            },
            'temperature': {
                label: "Temperatura (°C)",
                data: weatherData.map(d => d.temperature),
                borderColor: "#FFA07A", // Naranja claro
                backgroundColor: "rgba(255, 160, 122, 0.2)",
                dataType: 'temperature',
                yAxisID: 'y_temp'
            },
            'apparent-temperature': {
                label: "Sensación térmica (°C)",
                data: weatherData.map(d => d.apparent_temperature),
                borderColor: "#FF6347", // Naranja medio
                backgroundColor: "rgba(255, 99, 71, 0.2)",
                dataType: 'apparent-temperature',
                yAxisID: 'y_temp'
            },
            'weather-code': {
                label: "Clima",
                data: weatherData.map(d => d.weather_code),
                borderColor: "#F4A460", // Arena/Marrón claro
                backgroundColor: "rgba(255, 1, 1, 0.2)",
                dataType: 'weather-code',
                yAxisID: 'y_codigo'
            }
        }
    };

    initializeFilters();
    updateDatasets();
}

// Inicializa los filtros
function initializeFilters() {
    const checkboxes = document.querySelectorAll('.filtros input[type="checkbox"]');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateDatasets);
    });
}

// Actualiza los datasets mostrados en la gráfica
function updateDatasets() {
    const { chart, datasetConfigs } = window.chartConfig;
    const checkboxes = document.querySelectorAll('.filtros input[type="checkbox"]:checked');
    
    // Limpia los datasets actuales
    chart.data.datasets = [];
    
    // Obtiene los ejes Y activos
    const activeYAxes = new Set();
    
    // Añade un dataset por cada checkbox seleccionado
    checkboxes.forEach(checkbox => {
        const dataType = checkbox.dataset.type;
        const config = datasetConfigs[dataType];
        if (config) {
            chart.data.datasets.push({
                label: config.label,
                data: config.data,
                borderColor: config.borderColor,
                backgroundColor: config.backgroundColor,
                borderWidth: 3,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: "#fff",
                tension: 0.4,
                fill: true,
                dataType: config.dataType,
                yAxisID: config.yAxisID
            });
            activeYAxes.add(config.yAxisID);
        }
    });
    
    // Actualiza la visibilidad de los ejes Y
    Object.keys(chart.options.scales).forEach(scaleId => {
        if (scaleId.startsWith('y_')) {
            const showScale = activeYAxes.has(scaleId);
            chart.options.scales[scaleId].display = showScale;
        }
    });
      // Configura y actualiza la gráfica con animaciones
    chart.options.animation = {
        duration: 750,
        easing: 'easeInOutQuart',
        responsive: true,
        animateScale: true,
        animateRotate: true
    };
    chart.update();
}