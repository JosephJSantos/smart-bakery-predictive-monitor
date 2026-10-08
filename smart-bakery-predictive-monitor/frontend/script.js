async function loadData() {
    const res = await fetch("http://127.0.0.1:8000/data");
    const data = await res.json();
    const temps = data.map(d => d.temperature);

    const ctx = document.getElementById("chart").getContext("2d");
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: temps.map((_, i) => i),
            datasets: [{
                label: 'Temperatura',
                data: temps
            }]
        }
    });

    const pred = await fetch("http://127.0.0.1:8000/predict");
    const predData = await pred.json();

    if (predData.alert) {
        document.getElementById("status").innerText = "ALERTA CRÍTICO!";
        document.getElementById("status").classList.add("alert");
    }
}
