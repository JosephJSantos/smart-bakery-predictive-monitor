import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


def train_model(df: pd.DataFrame) -> LinearRegression:
    """Treina uma regressão linear para estimar a tendência da temperatura."""
    x = np.arange(len(df)).reshape(-1, 1)
    y = df["temperature"].to_numpy()
    model = LinearRegression()
    model.fit(x, y)
    return model


def predict_future(model: LinearRegression, future_steps: int = 10, last_index: int = 0) -> np.ndarray:
    """Prevê as próximas leituras com base no índice temporal."""
    future_index = np.arange(last_index + 1, last_index + future_steps + 1).reshape(-1, 1)
    return model.predict(future_index)
