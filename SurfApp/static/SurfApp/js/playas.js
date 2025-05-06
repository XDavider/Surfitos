// Muestra el modal para agregar una nueva playa
function agregarPlaya() {
    document.getElementById("modalAgregar").classList.add("show");
}

// Cierra el modal de agregar playa
function cerrarModal() {
    document.getElementById("modalAgregar").classList.remove("show");
}

// Elimina una playa de la base de datos usando su ID
function eliminarPlaya(id) {
    // Confirma con el usuario antes de eliminar
    if (!confirm("¿Estás seguro de que querés eliminar esta playa?")) return;

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
                alert("Playa eliminada correctamente");
                location.reload(); // Recarga la página para reflejar los cambios
            } else {
                alert("No se pudo eliminar la playa: " + data.error);
            }
        })
        .catch(() => alert("Error al conectar con el servidor"));
}

// Abre Google Maps en una nueva pestaña con las coordenadas dadas
function verEnMapa(lat, lon) {
    const url = `https://www.google.com/maps?q=${lat},${lon}`;
    window.open(url, '_blank');
}

// Simula solicitar información de una playa (puede conectarse con API más adelante)
function solicitarInfo(nombre) {
    alert('Solicitando info para: ' + nombre);
    // Aquí podrías hacer una solicitud a la API para obtener más info sobre la playa
}

function verDashboard(id) {
    window.open(`/dashboard/${id}/`, '_blank') ;
}

// Envía la nueva playa al backend para agregarla a la base de datos
function enviarNuevaPlaya() {
    // Obtiene los valores ingresados por el usuario
    const nombre = document.getElementById("inputNombre").value;
    const lugar = document.getElementById("inputLugar").value;

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
                alert("Playa agregada correctamente");
                cerrarModal(); // Cierra el modal tras el éxito
                location.reload(); // Recarga la página para ver la nueva playa
            } else {
                alert(data.error || "No se pudo agregar la playa");
            }
        })
        .catch(() => alert("Error al conectar con el servidor"));
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