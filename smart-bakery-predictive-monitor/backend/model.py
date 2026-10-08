import pandas as pd
from sklearn.linear_model import LinearRegression

def train_model(df):
    df["time_index"] = range(len(df))
    X = df[["time_index"]]
    y = df["temperature"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def predict_future(model, future_steps=10, last_index=0):
    future_index = [[last_index + i] for i in range(1, future_steps+1)]
    preds = model.predict(future_index)
    return preds
