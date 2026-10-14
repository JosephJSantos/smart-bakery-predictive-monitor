from pathlib import Path

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

try:
    from .model import predict_future, train_model
    from .simulator import generate_data
except ImportError:
    from model import predict_future, train_model
    from simulator import generate_data

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "simulated_data.csv"
ALERT_THRESHOLD = 10.0

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
    df = generate_data(output_path=DATA_PATH)
    return {"status": "ok", "message": "Novas leituras geradas.", "records": len(df)}
