from fastapi import FastAPI
import pandas as pd
from simulator import generate_data
from model import train_model, predict_future

app = FastAPI()

@app.get("/data")
def get_data():
    df = pd.read_csv("../data/simulated_data.csv")
    return df.tail(100).to_dict(orient="records")

@app.get("/predict")
def predict():
    df = pd.read_csv("../data/simulated_data.csv")
    model = train_model(df)
    preds = predict_future(model, last_index=len(df))
    alert = any(p > 10 for p in preds)
    return {"predictions": preds.tolist(), "alert": alert}

@app.get("/simulate")
def simulate():
    generate_data()
    return {"status": "new data generated"}
