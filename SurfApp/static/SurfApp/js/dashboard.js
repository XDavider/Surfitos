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
        scrollWheelZoom: true,  // Permite hacer zoom con la rueda del ratón
        doubleClickZoom: false, // Desactiva el zoom por doble clic
        boxZoom: false,         // Desactiva zoom por selección con caja
        keyboard: false,        // Desactiva navegación con teclado
        touchZoom: false        // Desactiva zoom con gestos táctiles
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