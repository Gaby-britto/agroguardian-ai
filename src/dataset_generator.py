import os

import numpy as np
import pandas as pd


# ==========================================================
# Reprodutibilidade
# ==========================================================

# Mantém os mesmos resultados entre execuções,
# facilitando testes e validações do projeto.

np.random.seed(42)


# ==========================================================
# Configurações do dataset
# ==========================================================

N_REGISTROS = 5000

DATA_DIRECTORY = "data"

DATASET_PATH = (
    f"{DATA_DIRECTORY}/dataset_agroguardian.csv"
)


# ==========================================================
# Níveis de risco
# ==========================================================

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"


# ==========================================================
# Limites - Umidade do solo
# ==========================================================

SOIL_RISK_MEDIUM_THRESHOLD = 50.0
SOIL_RISK_HIGH_THRESHOLD = 70.0
SOIL_RISK_CRITICAL_THRESHOLD = 85.0


# ==========================================================
# Limites - Inclinação
# ==========================================================

INCLINATION_RISK_MEDIUM_THRESHOLD = 5.0
INCLINATION_RISK_HIGH_THRESHOLD = 10.0
INCLINATION_RISK_CRITICAL_THRESHOLD = 15.0


# ==========================================================
# Limites - Distância do corpo d'água
# ==========================================================

WATER_RISK_CRITICAL_DISTANCE_M = 20.0
WATER_RISK_HIGH_DISTANCE_M = 50.0
WATER_RISK_MEDIUM_DISTANCE_M = 100.0


# ==========================================================
# Limites - Precipitação
# ==========================================================

PRECIPITATION_MEDIUM_THRESHOLD = 15.0
PRECIPITATION_HIGH_THRESHOLD = 30.0
PRECIPITATION_CRITICAL_THRESHOLD = 45.0


# ==========================================================
# Ordem dos riscos
# ==========================================================

# Permite comparar os níveis de risco pela severidade.

RISK_LEVELS = {
    RISK_LOW: 0,
    RISK_MEDIUM: 1,
    RISK_HIGH: 2,
    RISK_CRITICAL: 3
}


# ==========================================================
# Avaliação - Umidade do solo
# ==========================================================

def evaluate_soil_risk(
    soil_moisture: float
) -> str:

    if (
        soil_moisture
        > SOIL_RISK_CRITICAL_THRESHOLD
    ):
        return RISK_CRITICAL

    if (
        soil_moisture
        > SOIL_RISK_HIGH_THRESHOLD
    ):
        return RISK_HIGH

    if (
        soil_moisture
        > SOIL_RISK_MEDIUM_THRESHOLD
    ):
        return RISK_MEDIUM

    return RISK_LOW


# ==========================================================
# Avaliação - Inclinação
# ==========================================================

def evaluate_inclination_risk(
    inclination: float
) -> str:

    # O sinal indica apenas a direção da inclinação.
    # Para o risco operacional, utilizamos sua magnitude.

    absolute_inclination = abs(
        inclination
    )

    if (
        absolute_inclination
        > INCLINATION_RISK_CRITICAL_THRESHOLD
    ):
        return RISK_CRITICAL

    if (
        absolute_inclination
        > INCLINATION_RISK_HIGH_THRESHOLD
    ):
        return RISK_HIGH

    if (
        absolute_inclination
        > INCLINATION_RISK_MEDIUM_THRESHOLD
    ):
        return RISK_MEDIUM

    return RISK_LOW


# ==========================================================
# Avaliação - Distância do corpo d'água
# ==========================================================

def evaluate_water_risk(
    water_distance: float
) -> str:

    if (
        water_distance
        < WATER_RISK_CRITICAL_DISTANCE_M
    ):
        return RISK_CRITICAL

    if (
        water_distance
        < WATER_RISK_HIGH_DISTANCE_M
    ):
        return RISK_HIGH

    if (
        water_distance
        <= WATER_RISK_MEDIUM_DISTANCE_M
    ):
        return RISK_MEDIUM

    return RISK_LOW


# ==========================================================
# Avaliação - Precipitação
# ==========================================================

def evaluate_precipitation_risk(
    precipitation_mm: float
) -> str:

    if (
        precipitation_mm
        > PRECIPITATION_CRITICAL_THRESHOLD
    ):
        return RISK_CRITICAL

    if (
        precipitation_mm
        > PRECIPITATION_HIGH_THRESHOLD
    ):
        return RISK_HIGH

    if (
        precipitation_mm
        > PRECIPITATION_MEDIUM_THRESHOLD
    ):
        return RISK_MEDIUM

    return RISK_LOW


# ==========================================================
# Maior risco
# ==========================================================

def get_highest_risk(
    *risks: str
) -> str:

    return max(
        risks,
        key=lambda risk: RISK_LEVELS[risk]
    )


# ==========================================================
# Risco operacional dos sensores
# ==========================================================

def evaluate_sensor_operational_risk(
    soil_risk: str,
    pitch_risk: str,
    roll_risk: str,
    water_risk: str
) -> str:

    risks = [
        soil_risk,
        pitch_risk,
        roll_risk,
        water_risk
    ]

    # ------------------------------------------------------
    # Qualquer condição crítica
    # ------------------------------------------------------

    if RISK_CRITICAL in risks:
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Inclinação elevada + proximidade da água
    # ------------------------------------------------------

    # Uma inclinação elevada, seja longitudinal (pitch)
    # ou lateral (roll), combinada com proximidade elevada
    # de um corpo d'água representa condição crítica.

    if (
        water_risk == RISK_HIGH
        and (
            pitch_risk == RISK_HIGH
            or roll_risk == RISK_HIGH
        )
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Solo muito úmido + inclinação elevada
    # ------------------------------------------------------

    if (
        soil_risk == RISK_HIGH
        and (
            pitch_risk == RISK_HIGH
            or roll_risk == RISK_HIGH
        )
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Duas ou mais condições altas
    # ------------------------------------------------------

    high_count = risks.count(
        RISK_HIGH
    )

    if high_count >= 2:
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Duas ou mais condições médias
    # ------------------------------------------------------

    medium_count = risks.count(
        RISK_MEDIUM
    )

    if medium_count >= 2:
        return RISK_HIGH

    # ------------------------------------------------------
    # Maior risco individual
    # ------------------------------------------------------

    return get_highest_risk(
        *risks
    )


# ==========================================================
# Risco operacional final
# ==========================================================

def evaluate_operational_risk(
    sensor_operational_risk: str,
    precipitation_risk: str,
    soil_risk: str,
    pitch_risk: str,
    roll_risk: str,
    water_risk: str
) -> str:

    # ------------------------------------------------------
    # Condição crítica
    # ------------------------------------------------------

    if (
        RISK_CRITICAL
        in {
            sensor_operational_risk,
            precipitation_risk
        }
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Chuva elevada + solo muito úmido
    # ------------------------------------------------------

    if (
        precipitation_risk == RISK_HIGH
        and soil_risk == RISK_HIGH
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Chuva elevada + inclinação
    # ------------------------------------------------------

    if (
        precipitation_risk == RISK_HIGH
        and (
            pitch_risk == RISK_HIGH
            or roll_risk == RISK_HIGH
        )
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Chuva elevada + proximidade da água
    # ------------------------------------------------------

    if (
        precipitation_risk == RISK_HIGH
        and water_risk == RISK_HIGH
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Combinação das condições médias
    # ------------------------------------------------------

    risks = [
        soil_risk,
        pitch_risk,
        roll_risk,
        water_risk,
        precipitation_risk
    ]

    medium_count = risks.count(
        RISK_MEDIUM
    )

    if medium_count >= 2:
        return RISK_HIGH

    # ------------------------------------------------------
    # Maior risco entre sensores e clima
    # ------------------------------------------------------

    return get_highest_risk(
        sensor_operational_risk,
        precipitation_risk
    )


# ==========================================================
# Geração das variáveis primárias
# ==========================================================

# O dataset utiliza dois perfis de cenário:
#
# normal:
# representa condições mais comuns de operação.
#
# adverse:
# representa condições mais severas, garantindo que o
# dataset também contenha situações de maior risco.
#
# O tipo do cenário é utilizado somente durante a geração.
# Ele NÃO será incluído como variável de entrada do ML.

scenario_type = np.random.choice(
    [
        "normal",
        "adverse"
    ],
    size=N_REGISTROS,
    p=[
        0.75,
        0.25
    ]
)


# ==========================================================
# Estruturas auxiliares
# ==========================================================

# Cria os vetores que receberão os valores simulados
# de cada variável primária.

soil_moisture = np.zeros(
    N_REGISTROS
)

pitch = np.zeros(
    N_REGISTROS
)

roll = np.zeros(
    N_REGISTROS
)

water_distance = np.zeros(
    N_REGISTROS
)

precipitation_mm = np.zeros(
    N_REGISTROS
)


# ==========================================================
# Geração dos cenários
# ==========================================================

for index, scenario in enumerate(
    scenario_type
):

    # ------------------------------------------------------
    # Cenário normal
    # ------------------------------------------------------

    if scenario == "normal":

        # A umidade do solo fica concentrada em valores
        # baixos e intermediários, ainda permitindo
        # variações naturais.

        soil_moisture[index] = np.random.normal(
            loc=45,
            scale=15
        )

        # Terrenos com pequenas inclinações longitudinais
        # são mais frequentes durante operações normais.

        pitch[index] = np.random.normal(
            loc=0,
            scale=4
        )

        # Inclinações laterais também permanecem
        # predominantemente próximas de zero.

        roll[index] = np.random.normal(
            loc=0,
            scale=4
        )

        # A maior parte das operações normais ocorre
        # relativamente distante de corpos d'água.

        water_distance[index] = np.random.normal(
            loc=350,
            scale=180
        )

        # A precipitação acumulada tende a ser baixa
        # ou moderada em condições normais.

        precipitation_mm[index] = np.random.gamma(
            shape=1.8,
            scale=5.0
        )

    # ------------------------------------------------------
    # Cenário adverso
    # ------------------------------------------------------

    else:

        # Nos cenários adversos existe maior probabilidade
        # de o solo apresentar elevada umidade.

        soil_moisture[index] = np.random.normal(
            loc=75,
            scale=18
        )

        # Inclinações longitudinais mais severas possuem
        # maior probabilidade de ocorrência.

        pitch[index] = np.random.normal(
            loc=0,
            scale=14
        )

        # Inclinações laterais severas também passam
        # a aparecer com maior frequência.

        roll[index] = np.random.normal(
            loc=0,
            scale=12
        )

        # A distribuição exponencial aumenta a presença
        # de cenários próximos a corpos d'água.

        water_distance[index] = np.random.exponential(
            scale=100
        )

        # Cenários adversos apresentam maior probabilidade
        # de precipitação acumulada elevada.

        precipitation_mm[index] = np.random.gamma(
            shape=2.5,
            scale=10.0
        )


# ==========================================================
# Limitação das faixas
# ==========================================================

# Garante que os valores gerados permaneçam dentro das
# faixas utilizadas pela aplicação.

soil_moisture = np.clip(
    soil_moisture,
    0,
    100
)

pitch = np.clip(
    pitch,
    -40,
    40
)

roll = np.clip(
    roll,
    -40,
    40
)

water_distance = np.clip(
    water_distance,
    0,
    1000
)

precipitation_mm = np.clip(
    precipitation_mm,
    0,
    60
)


# ==========================================================
# Criação do DataFrame
# ==========================================================

# Somente as variáveis que realmente existirão na aplicação
# são adicionadas ao dataset.
#
# scenario_type não é incluído porque é apenas um recurso
# utilizado para controlar a geração dos dados sintéticos.

df = pd.DataFrame({
    "soil_moisture": soil_moisture,
    "pitch": pitch,
    "roll": roll,
    "water_distance": water_distance,
    "precipitation_mm": precipitation_mm
})


# ==========================================================
# Avaliação dos riscos individuais
# ==========================================================

df["soil_risk"] = (
    df["soil_moisture"]
    .apply(
        evaluate_soil_risk
    )
)

df["pitch_risk"] = (
    df["pitch"]
    .apply(
        evaluate_inclination_risk
    )
)

df["roll_risk"] = (
    df["roll"]
    .apply(
        evaluate_inclination_risk
    )
)

df["water_risk"] = (
    df["water_distance"]
    .apply(
        evaluate_water_risk
    )
)

df["precipitation_risk"] = (
    df["precipitation_mm"]
    .apply(
        evaluate_precipitation_risk
    )
)


# ==========================================================
# Risco operacional dos sensores
# ==========================================================

df["sensor_operational_risk"] = df.apply(
    lambda row: evaluate_sensor_operational_risk(
        soil_risk=row["soil_risk"],
        pitch_risk=row["pitch_risk"],
        roll_risk=row["roll_risk"],
        water_risk=row["water_risk"]
    ),
    axis=1
)


# ==========================================================
# Risco operacional final
# ==========================================================

df["operational_risk"] = df.apply(
    lambda row: evaluate_operational_risk(
        sensor_operational_risk=row[
            "sensor_operational_risk"
        ],
        precipitation_risk=row[
            "precipitation_risk"
        ],
        soil_risk=row[
            "soil_risk"
        ],
        pitch_risk=row[
            "pitch_risk"
        ],
        roll_risk=row[
            "roll_risk"
        ],
        water_risk=row[
            "water_risk"
        ]
    ),
    axis=1
)


# ==========================================================
# Exportação do dataset
# ==========================================================

os.makedirs(
    DATA_DIRECTORY,
    exist_ok=True
)

df.to_csv(
    DATASET_PATH,
    index=False
)


# ==========================================================
# Validação
# ==========================================================

print(
    "\nDataset gerado com sucesso!"
)

print(
    f"Arquivo salvo em: {DATASET_PATH}"
)

print(
    f"Total de registros: {len(df)}"
)


print(
    "\nDistribuição do risco operacional:"
)

print(
    df["operational_risk"]
    .value_counts()
)


print(
    "\nDistribuição percentual:"
)

print(
    (
        df["operational_risk"]
        .value_counts(
            normalize=True
        )
        * 100
    ).round(2)
)


print(
    "\nPrimeiras linhas:"
)

print(
    df.head()
)