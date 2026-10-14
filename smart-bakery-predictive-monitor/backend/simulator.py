from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd


def generate_data(n: int = 500, output_path: str | Path | None = None) -> pd.DataFrame:
    """Gera leituras IoT sintéticas de temperatura e umidade."""
    rng = np.random.default_rng()
    base_time = datetime.now().replace(second=0, microsecond=0)
    rows = []

    for i in range(n):
        # Simula aumento gradual de temperatura e uma piora após certo tempo.
        temperature = (
            5.0
            + 0.005 * i
            + 0.020 * max(i - 350, 0)
            + 0.35 * np.sin(i / 18)
            + rng.normal(0, 0.18)
        )
        humidity = (
            68
            + 2.5 * np.sin(i / 24)
            + 0.006 * i
            + rng.normal(0, 1.0)
        )
        rows.append({
            "timestamp": (base_time - timedelta(minutes=n - i - 1)).isoformat(timespec="seconds"),
            "temperature": round(float(temperature), 2),
            "humidity": round(float(np.clip(humidity, 35, 90)), 2),
        })

    df = pd.DataFrame(rows)
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
    return df
