from pathlib import Path

import joblib
import pandas as pd


# ==========================================================
# Caminhos da aplicação
# ==========================================================

# Localiza a raiz do projeto independentemente do diretório
# utilizado para executar a aplicação.

PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODEL_PATH = (
    PROJECT_ROOT
    / "models"
    / "operational_risk_model.joblib"
)


# ==========================================================
# Variáveis utilizadas pelo modelo
# ==========================================================

# Estas são as mesmas features utilizadas durante o
# treinamento do modelo.
#
# A ordem e os nomes devem permanecer consistentes com
# aqueles utilizados no model.py.

MODEL_FEATURES = [
    "soil_moisture",
    "pitch",
    "roll",
    "water_distance",
    "precipitation_mm"
]


# ==========================================================
# Pesos utilizados no score preditivo
# ==========================================================

# Cada classe de risco recebe um valor dentro da escala
# de 0 a 100.
#
# O score final será calculado utilizando as probabilidades
# retornadas pelo modelo para cada uma dessas classes.

RISK_SCORE_WEIGHTS = {
    "LOW": 0.0,
    "MEDIUM": 33.33,
    "HIGH": 66.67,
    "CRITICAL": 100.0
}


# ==========================================================
# Carregamento do modelo
# ==========================================================

def load_model():
    """
    Carrega o pipeline de Machine Learning treinado.

    O arquivo contém o pipeline completo utilizado no
    treinamento, incluindo:

    - tratamento de valores ausentes;
    - padronização das variáveis;
    - RandomForestClassifier.

    Dessa forma, a aplicação não precisa executar o
    pré-processamento manualmente durante a previsão.
    """

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Modelo de Machine Learning não encontrado. "
            "Execute o treinamento antes de realizar "
            "previsões."
        )

    return joblib.load(
        MODEL_PATH
    )


# ==========================================================
# Preparação dos dados para previsão
# ==========================================================

def prepare_prediction_data(
    readings: dict
) -> pd.DataFrame:
    """
    Converte o snapshot operacional em um DataFrame
    compatível com o pipeline de Machine Learning.

    Somente as variáveis primárias são enviadas ao modelo.

    Os riscos calculados pelas regras determinísticas não
    são utilizados como features para evitar vazamento de
    informação.
    """

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in readings
    ]

    if missing_features:
        raise ValueError(
            "Dados insuficientes para previsão. "
            "Campos ausentes: "
            + ", ".join(
                missing_features
            )
        )

    prediction_data = {
        feature: [
            readings[feature]
        ]
        for feature in MODEL_FEATURES
    }

    return pd.DataFrame(
        prediction_data
    )


# ==========================================================
# Previsão do risco operacional
# ==========================================================

def predict_operational_risk(
    readings: dict
) -> str:
    """
    Realiza a previsão do risco operacional utilizando
    o modelo de Machine Learning treinado.

    Fluxo:

    snapshot operacional
        ↓
    seleção das features
        ↓
    pipeline de pré-processamento
        ↓
    Random Forest
        ↓
    predicted_risk
    """

    model = load_model()

    prediction_data = (
        prepare_prediction_data(
            readings
        )
    )

    predicted_risk = (
        model.predict(
            prediction_data
        )[0]
    )

    return str(
        predicted_risk
    )


# ==========================================================
# Probabilidades das classes
# ==========================================================

def predict_risk_probabilities(
    readings: dict
) -> dict:
    """
    Retorna a probabilidade estimada pelo modelo para cada
    classe de risco.

    Exemplo:

    {
        "LOW": 0.02,
        "MEDIUM": 0.08,
        "HIGH": 0.76,
        "CRITICAL": 0.14
    }

    Esses valores poderão ser utilizados posteriormente para
    compor o score preditivo do projeto.
    """

    model = load_model()

    prediction_data = (
        prepare_prediction_data(
            readings
        )
    )

    probabilities = (
        model.predict_proba(
            prediction_data
        )[0]
    )

    classes = (
        model.classes_
    )

    return {
        str(risk_class): float(
            probability
        )
        for risk_class, probability
        in zip(
            classes,
            probabilities
        )
    }


# ==========================================================
# Score preditivo de risco
# ==========================================================

def calculate_predictive_risk_score(
    risk_probabilities: dict
) -> float:
    """
    Calcula um score preditivo de risco entre 0 e 100.

    O cálculo utiliza a probabilidade estimada pelo modelo
    para cada classe de risco e o peso correspondente à
    severidade dessa classe.

    Exemplo:

    LOW       = 10%
    MEDIUM    = 60%
    HIGH      = 25%
    CRITICAL  = 5%

    O resultado representa a severidade ponderada prevista
    pelo modelo.
    """

    score = 0.0

    for risk_level, weight in (
        RISK_SCORE_WEIGHTS.items()
    ):

        probability = (
            risk_probabilities.get(
                risk_level,
                0.0
            )
        )

        score += (
            probability
            * weight
        )

    # Limita o resultado à escala definida e
    # mantém duas casas decimais.

    score = max(
        0.0,
        min(
            score,
            100.0
        )
    )

    return round(
        score,
        2
    )


# ==========================================================
# Resultado completo da previsão
# ==========================================================

def get_prediction(
    readings: dict
) -> dict:
    """
    Executa a previsão completa do cenário operacional.

    O resultado contém:

    - classe de risco prevista;
    - score preditivo de 0 a 100;
    - probabilidades de cada classe.
    """

    model = load_model()

    prediction_data = (
        prepare_prediction_data(
            readings
        )
    )

    # ------------------------------------------------------
    # Classe prevista
    # ------------------------------------------------------

    predicted_risk = (
        model.predict(
            prediction_data
        )[0]
    )

    # ------------------------------------------------------
    # Probabilidades das classes
    # ------------------------------------------------------

    probabilities = (
        model.predict_proba(
            prediction_data
        )[0]
    )

    classes = (
        model.classes_
    )

    risk_probabilities = {
        str(risk_class): float(
            probability
        )
        for risk_class, probability
        in zip(
            classes,
            probabilities
        )
    }

    # ------------------------------------------------------
    # Score preditivo
    # ------------------------------------------------------

    predictive_risk_score = (
        calculate_predictive_risk_score(
            risk_probabilities
        )
    )

    # ------------------------------------------------------
    # Resultado
    # ------------------------------------------------------

    return {
        "predicted_risk": str(
            predicted_risk
        ),
        "predictive_risk_score":
            predictive_risk_score,
        "risk_probabilities":
            risk_probabilities
    }


# ==========================================================
# Score preditivo em lote
# ==========================================================

def calculate_predictive_risk_scores(
    probabilities,
    classes
) -> list[float]:
    """
    Calcula o score preditivo de risco para várias
    observações ao mesmo tempo.

    Cada linha de probabilities representa um cenário
    operacional e contém as probabilidades estimadas
    pelo modelo para todas as classes.

    O score é calculado utilizando a mesma lógica da
    previsão individual:

    LOW       → 0
    MEDIUM    → 33.33
    HIGH      → 66.67
    CRITICAL  → 100
    """

    scores = []

    for row_probabilities in probabilities:

        risk_probabilities = {
            str(risk_class): float(
                probability
            )
            for risk_class, probability
            in zip(
                classes,
                row_probabilities
            )
        }

        score = (
            calculate_predictive_risk_score(
                risk_probabilities
            )
        )

        scores.append(
            score
        )

    return scores


# ==========================================================
# Validação do DataFrame
# ==========================================================

def validate_prediction_dataframe(
    dataframe: pd.DataFrame
) -> None:
    """
    Valida se o DataFrame possui todas as variáveis
    necessárias para realizar previsões em lote.

    O dashboard poderá receber arquivos CSV externos.
    Por isso, esta validação impede que um arquivo
    incompatível seja enviado ao modelo.
    """

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in dataframe.columns
    ]

    if missing_features:
        raise ValueError(
            "Dataset incompatível com o modelo. "
            "Colunas ausentes: "
            + ", ".join(
                missing_features
            )
        )


# ==========================================================
# Previsão em lote
# ==========================================================

def predict_dataframe(
    dataframe: pd.DataFrame
) -> pd.DataFrame:
    """
    Executa previsões de Machine Learning para todas
    as linhas de um DataFrame.

    Esta função será utilizada principalmente pelo
    dashboard após o upload de um arquivo CSV.

    Fluxo:

    DataFrame
        ↓
    validação das features
        ↓
    pipeline treinado
        ↓
    classificação de risco
        ↓
    probabilidades
        ↓
    score preditivo
        ↓
    DataFrame enriquecido
    """

    # ------------------------------------------------------
    # Validação
    # ------------------------------------------------------

    validate_prediction_dataframe(
        dataframe
    )

    # ------------------------------------------------------
    # Cópia dos dados
    # ------------------------------------------------------

    # Trabalhamos sobre uma cópia para não modificar
    # diretamente o DataFrame recebido pela aplicação.

    enriched_dataframe = (
        dataframe.copy()
    )

    # ------------------------------------------------------
    # Carregamento do modelo
    # ------------------------------------------------------

    model = load_model()

    # ------------------------------------------------------
    # Seleção das features
    # ------------------------------------------------------

    prediction_data = (
        enriched_dataframe[
            MODEL_FEATURES
        ].copy()
    )

    # ------------------------------------------------------
    # Predição das classes
    # ------------------------------------------------------

    predictions = (
        model.predict(
            prediction_data
        )
    )

    # ------------------------------------------------------
    # Probabilidades das classes
    # ------------------------------------------------------

    probabilities = (
        model.predict_proba(
            prediction_data
        )
    )

    classes = (
        model.classes_
    )

    # ------------------------------------------------------
    # Score preditivo
    # ------------------------------------------------------

    predictive_scores = (
        calculate_predictive_risk_scores(
            probabilities,
            classes
        )
    )

    # ------------------------------------------------------
    # Inclusão das previsões no DataFrame
    # ------------------------------------------------------

    enriched_dataframe[
        "predicted_risk"
    ] = predictions

    enriched_dataframe[
        "predictive_risk_score"
    ] = predictive_scores

    # ------------------------------------------------------
    # Inclinação absoluta para visualização
    # ------------------------------------------------------

    # Para determinados gráficos do dashboard, utilizamos
    # a maior magnitude entre Pitch e Roll.
    #
    # Essa variável NÃO é utilizada pelo modelo de ML.
    # Ela existe somente para facilitar análises visuais.

    enriched_dataframe[
        "absolute_inclination"
    ] = (
        enriched_dataframe[
            [
                "pitch",
                "roll"
            ]
        ]
        .abs()
        .max(
            axis=1
        )
    )

    return enriched_dataframe