// Escuchador de eventos para cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa mini mapas satélite de fondo en cada tarjeta panorámica
    document.querySelectorAll('.playa-map-bg').forEach(el => {
        const lat = parseFloat(el.dataset.lat);
        const lon = parseFloat(el.dataset.lon);
        if (isNaN(lat) || isNaN(lon)) return;
        const miniMap = L.map(el, {
            center: [lat, lon],
            zoom: 13,
            zoomControl: false,
            attributionControl: false,
            dragging: false,
            scrollWheelZoom: false,
            doubleClickZoom: false,
            boxZoom: false,
            keyboard: false,
            touchZoom: false
        });
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 18
        }).addTo(miniMap);
        miniMap.panBy([-95, 0], { animate: false });
    });

    // Añade escuchadores de eventos para los clics en las tarjetas para permitir la navegación al dashboard
    const playaCards = document.querySelectorAll('.playa');
    playaCards.forEach(card => {
        const playaContent = card.querySelector('.playa-content');
        if (playaContent) {
            playaContent.addEventListener('click', function() {
                const id = card.dataset.id;
                verDashboard(id);
            });
        }
    });
});

let addMap = null;
let addMarker = null;
let selectedLat = null;
let selectedLon = null;
let editingPlayaId = null;
let selectedOlaOptima = null;
let selectedVientoOptimo = null;
let selectedMareaOptima = null;

const DIR_LABELS = { 0: 'N', 45: 'NE', 90: 'E', 135: 'SE', 180: 'S', 225: 'SO', 270: 'O', 315: 'NO' };

function setCompassValue(type, deg) {
    const ring = document.querySelector(`.compass-ring[data-compass="${type}"]`);
    const arrow = document.getElementById(`arrow-${type}`);
    const label = document.getElementById(`label-${type}`);
    if (!ring || !arrow || !label) return;

    ring.querySelectorAll('.dir-btn').forEach(b => b.classList.remove('active'));
    if (deg === null || deg === undefined) {
        arrow.style.transform = 'rotate(0deg)';
        arrow.style.opacity = '0.35';
        label.textContent = 'Sin definir';
        return;
    }
    const btn = ring.querySelector(`.dir-btn[data-deg="${deg}"]`);
    if (btn) btn.classList.add('active');
    arrow.style.opacity = '1';
    arrow.style.transform = `rotate(${deg}deg)`;
    label.textContent = `${DIR_LABELS[deg] || ''} (${deg}°)`;
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.compass-ring').forEach(ring => {
        const type = ring.dataset.compass;
        ring.querySelectorAll('.dir-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const deg = parseInt(btn.dataset.deg, 10);
                if (type === 'ola') {
                    selectedOlaOptima = selectedOlaOptima === deg ? null : deg;
                    setCompassValue('ola', selectedOlaOptima);
                } else {
                    selectedVientoOptimo = selectedVientoOptimo === deg ? null : deg;
                    setCompassValue('viento', selectedVientoOptimo);
                }
            });
        });
    });

    document.querySelectorAll('.tide-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const val = btn.dataset.tide;
            selectedMareaOptima = selectedMareaOptima === val ? null : val;
            setTideValue(selectedMareaOptima);
        });
    });
});

function setTideValue(val) {
    document.querySelectorAll('.tide-btn').forEach(b => {
        b.classList.toggle('active', Boolean(val && b.dataset.tide === val));
    });
}

function abrirModalPlaya(titulo, lat = 43.0, lon = -8.5, zoom = 6, hasPoint = false) {
    document.getElementById('titulo-modal-agregar').innerHTML = `<i class="fas fa-umbrella-beach"></i> ${titulo}`;
    document.getElementById("modalAgregar").classList.add("show");
    document.getElementById("inputNombre").focus();

    setTimeout(() => {
        if (!addMap) {
            addMap = L.map('mapa-agregar', { center: [lat, lon], zoom, zoomControl: true });
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                attribution: 'Tiles &copy; Esri',
                maxZoom: 19
            }).addTo(addMap);

            addMap.on('click', function(e) {
                selectedLat = e.latlng.lat;
                selectedLon = e.latlng.lng;
                if (addMarker) {
                    addMarker.setLatLng(e.latlng);
                } else {
                    addMarker = L.marker(e.latlng).addTo(addMap);
                }
                document.getElementById('coords-seleccionadas').textContent =
                    `Ubicación: ${selectedLat.toFixed(5)}, ${selectedLon.toFixed(5)}`;
            });
        } else {
            addMap.setView([lat, lon], zoom);
        }
        if (hasPoint) {
            if (addMarker) addMarker.setLatLng([lat, lon]);
            else addMarker = L.marker([lat, lon]).addTo(addMap);
            document.getElementById('coords-seleccionadas').textContent =
                `Ubicación: ${lat.toFixed(5)}, ${lon.toFixed(5)}`;
        }
        addMap.invalidateSize();
    }, 120);
}

// Muestra el modal para agregar una nueva playa con mapa interactivo
function agregarPlaya() {
    editingPlayaId = null;
    selectedOlaOptima = null;
    selectedVientoOptimo = null;
    selectedMareaOptima = null;
    setCompassValue('ola', null);
    setCompassValue('viento', null);
    setTideValue(null);
    const vivaEl = document.getElementById('inputMareaViva');
    if (vivaEl) vivaEl.checked = false;
    abrirModalPlaya('Añadir Playa');
}

// Muestra el modal precargado para editar una playa existente
function editarPlaya(id, nombre, lugar, lat, lon, olaOptima, vientoOptimo, mareaOptima, mareaViva) {
    if (window.event) window.event.stopPropagation();
    editingPlayaId = id;
    document.getElementById("inputNombre").value = nombre;
    document.getElementById("inputLugar").value = lugar;
    selectedLat = lat;
    selectedLon = lon;
    selectedOlaOptima = olaOptima;
    selectedVientoOptimo = vientoOptimo;
    selectedMareaOptima = mareaOptima || null;
    setCompassValue('ola', olaOptima);
    setCompassValue('viento', vientoOptimo);
    setTideValue(selectedMareaOptima);
    const vivaEl = document.getElementById('inputMareaViva');
    if (vivaEl) vivaEl.checked = Boolean(mareaViva);
    abrirModalPlaya('Editar Playa', lat, lon, 12, true);
}

// Cierra el modal de agregar/editar playa
function cerrarModal() {
    document.getElementById("modalAgregar").classList.remove("show");
    document.getElementById("inputNombre").value = '';
    document.getElementById("inputLugar").value = '';
    editingPlayaId = null;
    selectedLat = null;
    selectedLon = null;
    selectedOlaOptima = null;
    selectedVientoOptimo = null;
    if (addMarker && addMap) {
        addMap.removeLayer(addMarker);
        addMarker = null;
    }
    const coordsEl = document.getElementById('coords-seleccionadas');
    if (coordsEl) coordsEl.textContent = 'Ninguna ubicación seleccionada';
}

let playaIdAEliminar = null;

// Abre el modal propio de confirmación para eliminar una playa
function eliminarPlaya(id, nombre = '') {
    if (window.event) {
        window.event.stopPropagation();
    }
    playaIdAEliminar = id;
    const texto = document.getElementById('texto-confirmar-eliminar');
    if (texto) {
        texto.textContent = nombre
            ? `¿Seguro que quieres eliminar "${nombre}"? Esta acción no se puede deshacer.`
            : '¿Seguro que quieres eliminar esta playa? Esta acción no se puede deshacer.';
    }
    document.getElementById('modalEliminar').classList.add('show');
}

function cerrarModalEliminar() {
    playaIdAEliminar = null;
    document.getElementById('modalEliminar').classList.remove('show');
}

// Ejecuta la eliminación tras confirmar en el modal propio
function confirmarEliminarPlaya() {
    if (!playaIdAEliminar) return;
    const id = playaIdAEliminar;

    fetch(`/api/eliminar-playa/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(res => res.json())
    .then(data => {
        cerrarModalEliminar();
        if (data.ok) {
            showToast("Playa eliminada correctamente");
            const card = document.querySelector(`.playa[data-id="${id}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    card.remove();
                    if (document.querySelectorAll('.playa').length === 0) {
                        const emptyState = document.createElement('div');
                        emptyState.className = 'empty-state';
                        emptyState.innerHTML = `
                            <i class="fas fa-umbrella-beach"></i>
                            <p>No hay playas registradas.</p>
                            <p>¡Agrega tu primera playa!</p>
                        `;
                        document.getElementById('contenedor-playas').appendChild(emptyState);
                    }
                }, 300);
            }
        } else {
            showToast("Error: " + data.error, true);
        }
    })
    .catch(() => {
        cerrarModalEliminar();
        showToast("Error al conectar con el servidor", true);
    });
}

// Abre un mapa con Leaflet en un modal para mostrar la ubicación de la playa
function verEnMapa(lat, lon, nombre, lugar) {
    event.stopPropagation();
    
    // Set the modal title and show the modal
    document.getElementById('mapa-titulo').innerHTML = `<i class="fas fa-map-pin"></i> ${nombre}`;
    const modalMapa = document.getElementById('modalMapa');
    modalMapa.classList.add('show');
    
    // Initialize the map after the modal is visible
    setTimeout(() => {
        // Initialize the map with Leaflet
        const map = L.map('mapa-view', {
            center: [lat, lon],
            zoom: 13,
            zoomControl: true
        });
        
        // Mosaicos satélite (Esri World Imagery)
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles &copy; Esri',
            maxZoom: 19
        }).addTo(map);
        
        // Create a custom marker icon
        const markerIcon = L.divIcon({
            className: 'custom-marker',
            html: `<i class="fas fa-map-marker-alt" style="color: #ec6ead; font-size: 24px; text-shadow: 0 0 5px rgba(0,0,0,0.5);"></i>`,
            iconSize: [24, 24],
            iconAnchor: [12, 24]
        });
        
        // Add a marker at the beach location
        const marker = L.marker([lat, lon], { icon: markerIcon }).addTo(map);
        
        // Add a popup with beach info
        marker.bindPopup(`
            <strong>${nombre}</strong><br>
            ${lugar}<br>
            Lat: ${lat.toFixed(5)}, Lon: ${lon.toFixed(5)}
        `).openPopup();
        
        // Store the map instance in a global variable so we can destroy it later
        window.currentMap = map;
        
        // Fix any display issues with the map
        map.invalidateSize();
    }, 100);
}

// Close the map modal and clean up
function cerrarModalMapa() {
    const modalMapa = document.getElementById('modalMapa');
    modalMapa.classList.remove('show');
    
    // Destroy the map instance to prevent memory leaks
    if (window.currentMap) {
        window.currentMap.remove();
        window.currentMap = null;
    }
}

// Navigate to dashboard view for the selected beach
function verDashboard(id) {
    window.location.href = `/dashboard/${id}/`;
}

// Envía la nueva playa al backend para agregarla a la base de datos
function enviarNuevaPlaya() {
    const nombre = document.getElementById("inputNombre").value.trim();
    const lugar = document.getElementById("inputLugar").value.trim();

    if (!nombre) {
        showToast("Por favor ingresa un nombre para la playa", true);
        document.getElementById("inputNombre").focus();
        return;
    }

    if (selectedLat === null || selectedLon === null) {
        showToast("Haz clic en el mapa para marcar la ubicación", true);
        return;
    }

    const saveButton = document.querySelector('.btn.guardar');
    const originalText = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    saveButton.disabled = true;

    const url = editingPlayaId ? `/api/editar-playa/${editingPlayaId}` : '/api/agregar-playa/';
    const method = editingPlayaId ? 'PUT' : 'POST';

    fetch(url, {
        method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            nombre,
            lugar,
            latitud: selectedLat,
            longitud: selectedLon,
            ola_optima: selectedOlaOptima,
            viento_optimo: selectedVientoOptimo,
            marea_optima: selectedMareaOptima,
            marea_viva: Boolean(document.getElementById('inputMareaViva')?.checked)
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showToast("Playa agregada correctamente");
            cerrarModal(); // Cierra el modal tras el éxito
            
            // Instead of reloading, add the new beach to the DOM
            if (document.querySelector('.empty-state')) {
                document.querySelector('.empty-state').remove();
            }
            
            // Refresh the page to get the updated data
            location.reload();
        } else {
            showToast(data.error || "No se pudo agregar la playa", true);
        }
    })
    .catch(() => showToast("Error al conectar con el servidor", true))
    .finally(() => {
        // Reset button state
        saveButton.innerHTML = originalText;
        saveButton.disabled = false;
    });
}

// Toast notification function
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    
    if (isError) {
        toast.style.backgroundColor = '#e74c3c';
    } else {
        toast.style.backgroundColor = '#2ecc71';
    }
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Obtiene el valor del token CSRF almacenado en las cookies (necesario para Django)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Compara el nombre de la cookie con el buscado
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close modal when clicking outside the modal content
window.addEventListener('click', function(event) {
    const modal = document.getElementById('modalAgregar');
    if (event.target === modal) {
        cerrarModal();
    }
});

// Add keyboard support for modal
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModal();
    }
    
    if (event.key === 'Enter' && document.getElementById('modalAgregar').classList.contains('show')) {
        enviarNuevaPlaya();
    }
});