from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

try:  # funciona tanto com "uvicorn app:app" dentro de backend quanto como pacote
    from .model import predict_future, train_model
    from .simulator import generate_data
except ImportError:
    from model import predict_future, train_model
    from simulator import generate_data

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "simulated_data.csv"
ALERT_THRESHOLD = 10.0


class ScenarioRequest(BaseModel):
    temperature: float = Field(ge=-10, le=60, description="Temperatura alvo em °C")
    humidity: float = Field(ge=0, le=100, description="Umidade relativa alvo em %")
    readings: int = Field(default=20, ge=1, le=100, description="Quantidade de novas leituras")

app = FastAPI(
    title="Smart Bakery Predictive Monitor",
    description="API demonstrativa para dados IoT simulados e previsão de temperatura.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_dataset() -> pd.DataFrame:
    if not DATA_PATH.exists():
        generate_data(output_path=DATA_PATH)
    return pd.read_csv(DATA_PATH)


@app.on_event("startup")
def initialize_dataset():
    if not DATA_PATH.exists():
        generate_data(output_path=DATA_PATH)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/data")
def get_data():
    df = load_dataset().tail(100)
    return df.to_dict(orient="records")


@app.get("/predict")
def predict():
    df = load_dataset()
    # Usa as 100 leituras mais recentes para que a previsão acompanhe a tendência atual.
    recent = df.tail(100).reset_index(drop=True)
    model = train_model(recent)
    predictions = predict_future(model, future_steps=10, last_index=len(recent) - 1)
    values = [round(float(value), 2) for value in predictions]
    current_temperature = round(float(df["temperature"].iloc[-1]), 2)
    maximum_prediction = max(values)

    return {
        "model": "Regressão Linear (scikit-learn)",
        "predictions": values,
        "alert": maximum_prediction >= ALERT_THRESHOLD,
        "threshold": ALERT_THRESHOLD,
        "current_temperature": current_temperature,
        "maximum_prediction": maximum_prediction,
        "steps_ahead": len(values),
    }


@app.post("/simulate")
def simulate():
    """Reinicia o histórico com um conjunto de dados sintético normal."""
    df = generate_data(output_path=DATA_PATH)
    return {"status": "ok", "message": "Simulação padrão reiniciada.", "records": len(df)}


@app.post("/simulate/scenario")
def simulate_scenario(scenario: ScenarioRequest):
    """Acrescenta leituras que transitam da última medição até os valores escolhidos."""
    df = load_dataset()
    last_row = df.iloc[-1]
    last_timestamp = pd.to_datetime(last_row["timestamp"])
    start_temperature = float(last_row["temperature"])
    start_humidity = float(last_row["humidity"])
    rng = np.random.default_rng()
    new_rows = []

    for step in range(1, scenario.readings + 1):
        progress = step / scenario.readings
        temperature = start_temperature + (scenario.temperature - start_temperature) * progress
        humidity = start_humidity + (scenario.humidity - start_humidity) * progress
        new_rows.append({
            "timestamp": (last_timestamp + timedelta(minutes=step)).isoformat(timespec="seconds"),
            "temperature": round(float(temperature + rng.normal(0, 0.15)), 2),
            "humidity": round(float(np.clip(humidity + rng.normal(0, 0.8), 0, 100)), 2),
        })

    updated = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    updated.to_csv(DATA_PATH, index=False)
    return {
        "status": "ok",
        "message": "Cenário aplicado.",
        "target_temperature": scenario.temperature,
        "target_humidity": scenario.humidity,
        "new_readings": scenario.readings,
        "total_records": len(updated),
    }
