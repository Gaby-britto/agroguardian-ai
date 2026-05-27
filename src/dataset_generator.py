import pandas as pd
import numpy as np

np.random.seed(42)
n = 200

df = pd.DataFrame({
    "umidade": np.random.uniform(20, 90, n),
    "inclinacao": np.random.uniform(0, 30, n),
    "distancia_agua": np.random.uniform(10, 1000, n),
    "chuva": np.random.uniform(0, 50, n),
    "solo": np.random.choice(["arenoso", "argiloso", "misto"], n),
    "operacao": np.random.choice(["colheita", "plantio", "transporte"], n),
    "historico": np.random.randint(0, 5, n)
})

def calcular_risco(row):
    if row["distancia_agua"] < 50 or row["umidade"] > 80:
        return 3
    elif row["distancia_agua"] < 200:
        return 2
    elif row["distancia_agua"] < 500:
        return 1
    else:
        return 0

df["risco"] = df.apply(calcular_risco, axis=1)

df.to_csv("dataset_sompo.csv", index=False)
