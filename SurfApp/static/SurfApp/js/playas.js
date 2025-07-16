// Escuchador de eventos para cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
    // Añade escuchadores de eventos para los clics en las tarjetas
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

    // Añade el escuchador para el switch de filtrado
    const filtroFavoritas = document.getElementById('filtroFavoritas');
    if (filtroFavoritas) {
        filtroFavoritas.addEventListener('change', function() {
            // Cambiar el tema con una animación suave
            if (this.checked) {
                document.body.classList.add('favorites-theme');
                animateThemeChange(true);
                animarCambioTexto('Tus playas');
            } else {
                document.body.classList.remove('favorites-theme');
                animateThemeChange(false);
                animarCambioTexto('Todas las playas');
            }
            filtrarPlayas();
        });
    }

    // Añade el escuchador para la búsqueda
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filtrarPlayas();
        });
    }
});

// Función para filtrar las playas según el estado del switch y la búsqueda
function filtrarPlayas() {
    const filtroFavoritas = document.getElementById('filtroFavoritas');
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.toLowerCase().trim();
    const playas = document.querySelectorAll('.playa');
    const emptyState = document.querySelector('.empty-state');
    let playasVisibles = 0;

    playas.forEach(playa => {
        const esFavorita = playa.querySelector('.boton-favorito').classList.contains('favorito-activo');
        const nombre = playa.dataset.nombre.toLowerCase();
        const lugar = playa.dataset.lugar.toLowerCase();
        const coincideBusqueda = nombre.includes(searchTerm) || lugar.includes(searchTerm);

        if ((filtroFavoritas.checked && !esFavorita) || !coincideBusqueda) {
            playa.classList.add('oculta');
        } else {
            playa.classList.remove('oculta');
            playasVisibles++;
        }
    });

    // Mostrar mensaje cuando no hay playas que mostrar
    if (playasVisibles === 0) {
        if (!emptyState) {
            const nuevoEmptyState = document.createElement('div');
            nuevoEmptyState.className = 'empty-state';
            nuevoEmptyState.innerHTML = `
                <i class="fas fa-umbrella-beach"></i>
                <p>No hay playas ${filtroFavoritas.checked ? 'favoritas' : ''} para mostrar.</p>
                ${filtroFavoritas.checked ? '<p>¡Marca algunas playas como favoritas!</p>' : '<p>¡Agrega tu primera playa!</p>'}
            `;
            document.getElementById('contenedor-playas').appendChild(nuevoEmptyState);
        }
    } else if (emptyState) {
        emptyState.remove();
    }
}

// Muestra el modal para agregar una nueva playa
function agregarPlaya() {
    document.getElementById("modalAgregar").classList.add("show");
    document.getElementById("inputNombre").focus();
}

// Cierra el modal de agregar playa
function cerrarModal() {    document.getElementById("modalAgregar").classList.remove("show");
    // Limpia los campos de entrada
    document.getElementById("inputNombre").value = '';
    document.getElementById("inputLugar").value = '';
}

// Elimina una playa de la base de datos usando su ID
function eliminarPlaya(button) {
    // Evita la propagación del evento
    event.stopPropagation();
    
    const playaCard = button.closest('.playa');
    const id = playaCard.dataset.id;
    
    // Confirma con el usuario antes de eliminar
    if (!confirm("¿Estás seguro de que quieres eliminar esta playa?")) return;

    // Realiza una solicitud DELETE al backend
    fetch(`/api/eliminar-playa/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Token CSRF para protección Django
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            showToast("Playa eliminada correctamente");
              // Elimina la tarjeta con animación en lugar de recargar
            const card = document.querySelector(`.playa[data-id="${id}"]`);
            if (card) {
                card.style.opacity = '0';
                card.style.transform = 'scale(0.8)';
                setTimeout(() => {
                    card.remove();
                    // Check if there are no more beaches
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
    .catch(() => showToast("Error al conectar con el servidor", true));
}

// Abre un mapa con Leaflet en un modal para mostrar la ubicación de la playa
function verEnMapa(button) {
    event.stopPropagation();
    
    const playaCard = button.closest('.playa');
    const nombre = playaCard.dataset.nombre;
    const lugar = playaCard.dataset.lugar;
    const lat = parseFloat(playaCard.dataset.lat);
    const lon = parseFloat(playaCard.dataset.lon);
    
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
        
        // Use OpenStreetMap tiles directly
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
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
function verDashboard(button) {
    event.stopPropagation();
    const playaCard = button.closest('.playa');
    const id = playaCard.dataset.id;
    window.location.href = `/dashboard/${id}/`;
}

// Función para marcar/desmarcar una playa como favorita
function toggleFavorito(button) {
    event.stopPropagation();
    const playaCard = button.closest('.playa');
    const id = playaCard.dataset.id;

    fetch(`/api/toggle-favorita/${id}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.ok) {
            if (data.is_favorita) {
                button.classList.add('favorito-activo');
                button.title = 'Quitar de favoritos';
                showToast('Playa añadida a favoritos');
            } else {
                button.classList.remove('favorito-activo');
                button.title = 'Añadir a favoritos';
                showToast('Playa eliminada de favoritos');
            }
        } else {
            showToast('Error al actualizar favoritos: ' + data.error, true);
        }
    })
    .catch(() => showToast('Error al conectar con el servidor', true));
}

// Envía la nueva playa al backend para agregarla a la base de datos
function enviarNuevaPlaya() {
    // Obtiene los valores ingresados por el usuario
    const nombre = document.getElementById("inputNombre").value.trim();
    const lugar = document.getElementById("inputLugar").value.trim();
    
    // Basic validation
    if (!nombre) {
        showToast("Por favor ingresa un nombre para la playa", true);
        document.getElementById("inputNombre").focus();
        return;
    }
    
    if (!lugar) {
        showToast("Por favor ingresa la ubicación de la playa", true);
        document.getElementById("inputLugar").focus();
        return;
    }

    // Show loading state
    const saveButton = document.querySelector('.btn.guardar');
    const originalText = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Guardando...';
    saveButton.disabled = true;

    // Realiza una solicitud POST al backend con los datos ingresados
    fetch('/api/agregar-playa/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Necesario para Django
        },
        body: JSON.stringify({nombre, lugar}) // Enviamos los datos en formato JSON
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

// Función para animar el cambio de tema
function animateThemeChange(isFavorites) {
    // Elementos que necesitan animación especial
    const header = document.querySelector('.header');
    const addButton = document.querySelector('.agregar');
    const container = document.querySelector('.container');
    
    // Transición suave del header sin escalado
    if (header) {
        header.style.opacity = '0.8';
        setTimeout(() => {
            header.style.opacity = '1';
        }, 300);
    }
    
    // Animar el botón de agregar
    if (addButton) {
        addButton.style.transform = 'scale(0.95) rotate(-180deg)';
        setTimeout(() => {
            addButton.style.transform = 'scale(1) rotate(0)';
        }, 500);
    }
    
    // Animar el contenedor principal
    if (container) {
        container.style.transform = 'scale(0.98)';
        container.style.opacity = '0.9';
        setTimeout(() => {
            container.style.transform = 'scale(1)';
            container.style.opacity = '1';
        }, 300);
    }
    
    // Animar las tarjetas de playas con efecto cascada
    const playas = document.querySelectorAll('.playa:not(.oculta)');
    playas.forEach((playa, index) => {
        playa.style.transform = 'scale(0.9) translateY(20px)';
        playa.style.opacity = '0';
        
        setTimeout(() => {
            playa.style.transform = 'scale(1) translateY(0)';
            playa.style.opacity = '1';
        }, 100 + (index * 100));
    });

    // Mostrar un mensaje toast con el cambio
    showToast(isFavorites ? '🌟 Mostrando favoritas' : '🏖️ Mostrando todas las playas');
}

// Función para animar el cambio de texto del título letra por letra
async function animarCambioTexto(nuevoTexto) {
    const titulo = document.getElementById('titulo-playas');
    const textoActual = titulo.textContent;
    titulo.classList.add('typing');

    // Borrar texto actual letra por letra
    for (let i = textoActual.length; i >= 0; i--) {
        titulo.textContent = textoActual.substring(0, i);
        await new Promise(resolve => setTimeout(resolve, 25));
    }

    // Escribir nuevo texto letra por letra
    for (let i = 0; i <= nuevoTexto.length; i++) {
        titulo.textContent = nuevoTexto.substring(0, i);
        await new Promise(resolve => setTimeout(resolve, 25));
    }

    titulo.classList.remove('typing');
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