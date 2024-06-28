document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start');
    const stopButton = document.getElementById('stop');
    const pauseButton = document.getElementById('pause');
    const resumeButton = document.getElementById('resume');
    const fareDisplay = document.getElementById('fare');
    const historySection = document.getElementById('history');

    let intervalId;

    function updateFare() {
        fetch('/fare')
            .then(response => response.json())
            .then(data => {
                fareDisplay.textContent = data.fare.toFixed(2);
            });
    }

    function updateHistory() {
        fetch('/history')
            .then(response => response.json())
            .then(data => {
                const historyHtml = data.history.map(ride => `
                    <div class="ride-entry">
                        <p><strong>Usuario:</strong> ${ride.usuario}</p>
                        <p><strong>Inicio:</strong> ${ride.inicio}</p>
                        <p><strong>Fin:</strong> ${ride.fin}</p>
                        <p><strong>Total:</strong> ${ride.total}</p>
                    </div>
                `).join('');
                historySection.innerHTML = `
                    <h2><i class="fas fa-history"></i> Historial de Viajes (Últimos 10)</h2>
                    <div class="history-container">
                        ${historyHtml}
                    </div>
                `;
            });
    }

    startButton.addEventListener('click', function() {
        fetch('/start', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                startButton.disabled = true;
                stopButton.disabled = false;
                pauseButton.disabled = false;
                intervalId = setInterval(updateFare, 1000);
            });
    });

    stopButton.addEventListener('click', function() {
        fetch('/finish', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                fareDisplay.textContent = data.fare.toFixed(2);
                startButton.disabled = false;
                stopButton.disabled = true;
                pauseButton.disabled = true;
                resumeButton.disabled = true;
                clearInterval(intervalId);
                updateHistory();
            });
    });

    pauseButton.addEventListener('click', function() {
        fetch('/stop', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                pauseButton.disabled = true;
                resumeButton.disabled = false;
                clearInterval(intervalId);
            });
    });

    resumeButton.addEventListener('click', function() {
        fetch('/continue', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                pauseButton.disabled = true;
                resumeButton.disabled = true;
                intervalId = setInterval(updateFare, 1000);
            });
    });

    updateHistory();
});