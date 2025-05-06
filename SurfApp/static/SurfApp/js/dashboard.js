

document.addEventListener("DOMContentLoaded", function () {
    const coordDiv = document.getElementById("coord");
    const lat = parseFloat(coordDiv.dataset.lat);
    const lon = parseFloat(coordDiv.dataset.lon);

    const map = L.map('mapa-playa', {
        center: [lat, lon],
        zoom: 15,
        zoomControl: false,
        dragging: false,
        scrollWheelZoom: true,
        doubleClickZoom: false,
        boxZoom: false,
        keyboard: false,
        touchZoom: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '',
        maxZoom: 28,
    }).addTo(map);

    L.marker([lat, lon]).addTo(map);

    setTimeout(() => {
        map.invalidateSize({pan: false});
    }, 300);
});

function actualizarHora() {
    const ahora = new Date();
    const opciones = {year: 'numeric', month: 'long', day: 'numeric'};
    const fecha = ahora.toLocaleDateString('es-ES', opciones);
    const hora = ahora.toLocaleTimeString('es-ES', {hour: '2-digit', minute: '2-digit'});
    document.getElementById('hora-actual').textContent = `${fecha} - ${hora}`;
}

document.addEventListener("DOMContentLoaded", actualizarHora);
