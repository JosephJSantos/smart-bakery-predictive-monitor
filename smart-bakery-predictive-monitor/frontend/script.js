const API_URL = "http://127.0.0.1:8000";
let temperatureChart = null;
let humidityChart = null;

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, options);
  if (!response.ok) throw new Error(`A API respondeu com status ${response.status}.`);
  return response.json();
}

function renderChart(data, predictions) {
  const historyLabels = data.map((row) => {
    const date = new Date(row.timestamp);
    return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  });
  const forecastLabels = predictions.predictions.map((_, index) => `+${index + 1}`);
  const labels = [...historyLabels, ...forecastLabels];
  const historyValues = data.map((row) => row.temperature);
  const forecastValues = Array(data.length - 1).fill(null)
    .concat([data[data.length - 1].temperature, ...predictions.predictions]);

  if (temperatureChart) temperatureChart.destroy();
  temperatureChart = new Chart($("chart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Temperatura observada (°C)",
          data: [...historyValues, ...Array(predictions.predictions.length).fill(null)],
          borderColor: "#2459d3",
          backgroundColor: "rgba(36, 89, 211, 0.10)",
          fill: true,
          tension: 0.25,
          pointRadius: 0,
          borderWidth: 2
        },
        {
          label: "Previsão (°C)",
          data: forecastValues,
          borderColor: "#e28b28",
          backgroundColor: "#e28b28",
          borderDash: [6, 5],
          tension: 0.2,
          pointRadius: 3,
          pointBackgroundColor: "#e28b28",
          fill: false,
          borderWidth: 2
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { ticks: { maxTicksLimit: 10, maxRotation: 0 }, grid: { display: false } },
        y: { title: { display: true, text: "Temperatura (°C)" } }
      }
    }
  });
}

function renderHumidityChart(data) {
  const labels = data.map((row) => {
    const date = new Date(row.timestamp);
    return date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
  });
  if (humidityChart) humidityChart.destroy();
  humidityChart = new Chart($("humidityChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Umidade relativa (%)",
        data: data.map((row) => row.humidity),
        borderColor: "#168578",
        backgroundColor: "rgba(22, 133, 120, 0.12)",
        fill: true,
        tension: 0.25,
        pointRadius: 0,
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { ticks: { maxTicksLimit: 10, maxRotation: 0 }, grid: { display: false } },
        y: { min: 0, max: 100, title: { display: true, text: "Umidade relativa (%)" } }
      }
    }
  });
}

function renderStatus(prediction) {
  const panel = document.querySelector(".status-panel");
  panel.classList.remove("ok", "alert");
  if (prediction.alert) {
    panel.classList.add("alert");
    $("statusTitle").textContent = "Alerta de temperatura";
    $("statusDescription").textContent =
      `O modelo prevê temperatura de até ${prediction.maximum_prediction} °C, acima do limite de ${prediction.threshold} °C.`;
  } else {
    panel.classList.add("ok");
    $("statusTitle").textContent = "Condições dentro do limite";
    $("statusDescription").textContent =
      `A previsão máxima é ${prediction.maximum_prediction} °C; limite configurado: ${prediction.threshold} °C.`;
  }
}

async function loadData() {
  $("errorMessage").textContent = "";
  $("refreshButton").disabled = true;
  try {
    const [data, prediction] = await Promise.all([api("/data"), api("/predict")]);
    if (!data.length) throw new Error("A API não retornou leituras.");
    const latest = data[data.length - 1];

    $("currentTemp").textContent = Number(latest.temperature).toFixed(1);
    $("currentHumidity").textContent = Number(latest.humidity).toFixed(1);
    $("predictedTemp").textContent = Number(prediction.maximum_prediction).toFixed(1);
    $("recordCount").textContent = data.length;
    $("updatedAt").textContent = `Atualizado às ${new Date().toLocaleTimeString("pt-BR")}`;
    renderStatus(prediction);
    renderChart(data, prediction);
    renderHumidityChart(data);
  } catch (error) {
    $("statusTitle").textContent = "Não foi possível conectar à API";
    $("statusDescription").textContent = "Confira se o FastAPI está rodando em http://127.0.0.1:8000.";
    $("errorMessage").textContent = error.message;
  } finally {
    $("refreshButton").disabled = false;
  }
}

async function simulateData() {
  $("simulateButton").disabled = true;
  $("errorMessage").textContent = "";
  try {
    await api("/simulate", { method: "POST" });
    await loadData();
  } catch (error) {
    $("errorMessage").textContent = `Não foi possível gerar dados: ${error.message}`;
  } finally {
    $("simulateButton").disabled = false;
  }
}

async function applyScenario(temperature, humidity, readings) {
  $("applyScenarioButton").disabled = true;
  $("errorMessage").textContent = "";
  try {
    await api("/simulate/scenario", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ temperature, humidity, readings })
    });
    await loadData();
  } catch (error) {
    $("errorMessage").textContent = `Não foi possível aplicar o cenário: ${error.message}`;
  } finally {
    $("applyScenarioButton").disabled = false;
  }
}

$("applyScenarioButton").addEventListener("click", () => {
  const temperature = Number($("scenarioTemp").value);
  const humidity = Number($("scenarioHumidity").value);
  const readings = Number($("scenarioReadings").value);
  if (!Number.isFinite(temperature) || temperature < -10 || temperature > 60 ||
      !Number.isFinite(humidity) || humidity < 0 || humidity > 100) {
    $("errorMessage").textContent = "Use temperatura entre -10 e 60 °C e umidade entre 0 e 100%.";
    return;
  }
  applyScenario(temperature, humidity, readings);
});

document.querySelectorAll("[data-preset]").forEach((button) => {
  button.addEventListener("click", () => {
    const currentTemperature = Number($("currentTemp").textContent) || 5;
    const currentHumidity = Number($("currentHumidity").textContent) || 68;
    const presets = {
      cold: { temperature: -5, humidity: currentHumidity },
      hot: { temperature: 45, humidity: currentHumidity },
      humid: { temperature: currentTemperature, humidity: 95 },
      dry: { temperature: currentTemperature, humidity: 10 }
    };
    const preset = presets[button.dataset.preset];
    $("scenarioTemp").value = preset.temperature;
    $("scenarioHumidity").value = preset.humidity;
    applyScenario(preset.temperature, preset.humidity, Number($("scenarioReadings").value));
  });
});

$("resetScenarioButton").addEventListener("click", async () => {
  if (!confirm("Isso vai substituir o histórico atual pelos dados sintéticos normais. Continuar?")) return;
  await simulateData();
});

$("refreshButton").addEventListener("click", loadData);
$("simulateButton").addEventListener("click", simulateData);
loadData();
