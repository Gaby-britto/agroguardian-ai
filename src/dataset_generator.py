import pandas as pd
import numpy as np
import os

# Reprodutibilidade dos resultados
np.random.seed(42)

# Quantidade de registros simulados
N_REGISTROS = 1000

# ----------------------------------------------------------
# Geração das variáveis
# ----------------------------------------------------------

df = pd.DataFrame({
    "umidade": np.random.uniform(20, 95, N_REGISTROS),
    "inclinacao": np.random.uniform(0, 35, N_REGISTROS),
    "distancia_agua": np.random.uniform(10, 1000, N_REGISTROS),
    "chuva": np.random.uniform(0, 60, N_REGISTROS),
    "solo": np.random.choice(
        ["arenoso", "argiloso", "misto"],
        N_REGISTROS,
        p=[0.30, 0.40, 0.30]
    ),
    "operacao": np.random.choice(
        ["plantio", "colheita", "transporte"],
        N_REGISTROS
    ),
    "historico": np.random.randint(0, 6, N_REGISTROS)
})

# ----------------------------------------------------------
# Cálculo do Score de Risco
# ----------------------------------------------------------

def calcular_risco(row):

    score = 0

    # Umidade do solo
    if row["umidade"] > 85:
        score += 3
    elif row["umidade"] > 70:
        score += 2
    elif row["umidade"] > 50:
        score += 1

    # Distância de corpos d'água
    if row["distancia_agua"] < 50:
        score += 3
    elif row["distancia_agua"] < 200:
        score += 2
    elif row["distancia_agua"] < 500:
        score += 1

    # Chuva acumulada
    if row["chuva"] > 45:
        score += 3
    elif row["chuva"] > 30:
        score += 2
    elif row["chuva"] > 15:
        score += 1

    # Inclinação do terreno
    if row["inclinacao"] > 25:
        score += 2
    elif row["inclinacao"] > 15:
        score += 1

    # Histórico de incidentes
    if row["historico"] >= 4:
        score += 2
    elif row["historico"] >= 2:
        score += 1

    # Tipo de solo
    if row["solo"] == "argiloso":
        score += 2
    elif row["solo"] == "misto":
        score += 1

    # Tipo de operação
    if row["operacao"] == "colheita":
        score += 1

    # Classificação final
    if score >= 12:
        return "Critico"
    elif score >= 8:
        return "Alto"
    elif score >= 4:
        return "Medio"
    else:
        return "Baixo"

# ----------------------------------------------------------
# Aplicação da classificação
# ----------------------------------------------------------

df["risco"] = df.apply(calcular_risco, axis=1)

# ----------------------------------------------------------
# Cria pasta data e exporta CSV
# ----------------------------------------------------------

os.makedirs("data", exist_ok=True)

CAMINHO_DATASET = "data/dataset_sompo.csv"

df.to_csv(CAMINHO_DATASET, index=False)

# ----------------------------------------------------------
# Informações de validação
# ----------------------------------------------------------

print(" Dataset gerado com sucesso!")
print(f" Arquivo salvo em: {CAMINHO_DATASET}")
print(f" Total de registros: {len(df)}")

print("\n Distribuição dos riscos:")
print(df["risco"].value_counts())

print("\n Primeiras linhas:")
print(df.head())