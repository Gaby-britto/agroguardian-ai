# ==========================================================
# Níveis de risco
# ==========================================================

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"


# ==========================================================
# Limites de precipitação
# ==========================================================

# <= 15 mm        → Baixo
# > 15 até 30 mm  → Médio
# > 30 até 45 mm  → Alto
# > 45 mm         → Crítico

PRECIPITATION_MEDIUM_THRESHOLD = 15.0
PRECIPITATION_HIGH_THRESHOLD = 30.0
PRECIPITATION_CRITICAL_THRESHOLD = 45.0


# ==========================================================
# Ordem dos níveis de risco
# ==========================================================

# Valor numérico utilizado internamente para comparar
# a severidade entre diferentes níveis de risco.

RISK_LEVELS = {
    RISK_LOW: 0,
    RISK_MEDIUM: 1,
    RISK_HIGH: 2,
    RISK_CRITICAL: 3
}


# ==========================================================
# Avaliação da precipitação
# ==========================================================

def evaluate_precipitation_risk(
    precipitation_mm: float
) -> str:
    """
    Classifica o risco associado à precipitação acumulada.

    O valor recebido representa a quantidade de chuva
    acumulada em milímetros.
    """

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
# Maior nível de risco
# ==========================================================

def get_highest_risk(
    *risks: str
) -> str:
    """
    Retorna o maior nível de risco entre os valores
    recebidos.

    Exemplo:
    LOW + MEDIUM + HIGH → HIGH
    """

    return max(
        risks,
        key=lambda risk: RISK_LEVELS[risk]
    )


# ==========================================================
# Avaliação do risco operacional completo
# ==========================================================

def evaluate_operational_risk(
    sensor_operational_risk: str,
    precipitation_risk: str,
    soil_risk: str,
    pitch_risk: str,
    roll_risk: str,
    water_risk: str
) -> str:
    """
    Consolida os riscos obtidos pelos sensores do ESP32
    com o risco proveniente dos dados climáticos.

    O sensor_operational_risk representa o risco já
    calculado pelo ESP32 considerando:

    - umidade do solo;
    - inclinação longitudinal (pitch);
    - inclinação lateral (roll);
    - distância do corpo d'água.

    A precipitação é adicionada posteriormente pelo Python,
    pois sua origem será uma API climática externa.
    """

    # ------------------------------------------------------
    # Condição crítica individual
    # ------------------------------------------------------

    # Caso os sensores já tenham identificado uma condição
    # crítica ou a precipitação esteja em nível crítico,
    # o risco operacional final também será crítico.

    if (
        RISK_CRITICAL
        in {
            sensor_operational_risk,
            precipitation_risk
        }
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Precipitação alta + solo muito úmido
    # ------------------------------------------------------

    # A combinação de precipitação elevada com alta
    # umidade do solo aumenta o risco de perda de tração,
    # compactação, formação de sulcos e atolamento.

    if (
        precipitation_risk == RISK_HIGH
        and soil_risk == RISK_HIGH
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Precipitação alta + inclinação elevada
    # ------------------------------------------------------

    # Chuva elevada combinada com inclinação longitudinal
    # ou lateral aumenta o risco de deslizamento e perda
    # de estabilidade da máquina.

    if (
        precipitation_risk == RISK_HIGH
        and (
            pitch_risk == RISK_HIGH
            or roll_risk == RISK_HIGH
        )
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Precipitação alta + proximidade da água
    # ------------------------------------------------------

    # Precipitação elevada próxima a um corpo d'água pode
    # aumentar a instabilidade do terreno e o risco de
    # aproximação de margens ou áreas alagadas.

    if (
        precipitation_risk == RISK_HIGH
        and water_risk == RISK_HIGH
    ):
        return RISK_CRITICAL

    # ------------------------------------------------------
    # Combinação das condições avaliadas
    # ------------------------------------------------------

    risks = [
        soil_risk,
        pitch_risk,
        roll_risk,
        water_risk,
        precipitation_risk
    ]

    # ------------------------------------------------------
    # Duas ou mais condições médias
    # ------------------------------------------------------

    # Mesmo sem uma condição individual grave, múltiplos
    # fatores moderados simultâneos representam uma situação
    # operacional que exige maior atenção.

    medium_risk_count = risks.count(
        RISK_MEDIUM
    )

    if medium_risk_count >= 2:
        return RISK_HIGH

    # ------------------------------------------------------
    # Maior risco identificado
    # ------------------------------------------------------

    # Quando nenhuma das regras combinatórias anteriores
    # for atendida, utiliza o maior risco entre a avaliação
    # realizada pelos sensores e a precipitação.

    return get_highest_risk(
        sensor_operational_risk,
        precipitation_risk
    )