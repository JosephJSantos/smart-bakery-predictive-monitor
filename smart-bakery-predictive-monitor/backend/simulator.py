import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_data(n=500):
    base_time = datetime.now()
    data = []
    temp = 5
    humidity = 70

    for i in range(n):
        temp += np.random.normal(0, 0.2)
        humidity += np.random.normal(0, 0.5)

        if i > 350:
            temp += 0.05

        data.append({
            "timestamp": base_time + timedelta(minutes=i),
            "temperature": temp,
            "humidity": humidity
        })

    df = pd.DataFrame(data)
    os.makedirs("../data", exist_ok=True)
    df.to_csv("../data/simulated_data.csv", index=False)
    return df
