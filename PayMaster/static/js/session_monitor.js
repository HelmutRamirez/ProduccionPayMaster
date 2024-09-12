var idleTime = 0;

function timerIncrement() {
    idleTime++;
    if (idleTime > 1) { // 1 minuto
        window.location.href = redirectUrl;
    }
}

$(document).ready(function () {
    // Increment the idle time counter every 10 seconds.
    var idleInterval = setInterval(timerIncrement, 10000); // 10 segundos

    // Reset the idle timer on mouse movement or key press.
    $(this).mousemove(function (e) {
        idleTime = 0;
        keepSessionAlive();
    });
    $(this).keypress(function (e) {
        idleTime = 0;
        keepSessionAlive();
    });
});

function keepSessionAlive() {
    $.get(keepSessionAliveUrl);
}

window.addEventListener('popstate', function (event) {
    // Prevenir el comportamiento por defecto
    event.preventDefault();

    // Enviar la solicitud POST para cerrar sesión
    fetch(redirectUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({})
    }).then(response => {
        if (response.ok) {
            // Redirigir a la página de inicio de sesión después de cerrar sesión
            window.location.href = loginUrl;
        }
    }).catch(error => {
        console.error('Error al cerrar sesión:', error);
        // Opcional: Manejar errores si es necesario
    });
});
