import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ==========================================================
# Configuração de caminhos
# ==========================================================

# Localiza a raiz do projeto a partir da pasta dashboard/.
PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

SRC_DIRECTORY = (
    PROJECT_ROOT
    / "src"
)

DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "dataset_agroguardian.csv"
)


# Permite importar os módulos localizados dentro de src/.
if str(SRC_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(SRC_DIRECTORY)
    )


# ==========================================================
# Imports da aplicação
# ==========================================================

from ml.prediction_service import (
    get_prediction,
    predict_dataframe
)

from risk.risk_service import (
    evaluate_precipitation_risk,
    evaluate_operational_risk
)


# ==========================================================
# Configuração da página
# ==========================================================

st.set_page_config(
    page_title="AgroGuardian AI",
    page_icon="🌱",
    layout="wide"
)


# ==========================================================
# Constantes do dashboard
# ==========================================================

RISK_ORDER = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]

RISK_LABELS = {
    "LOW": "Baixo",
    "MEDIUM": "Médio",
    "HIGH": "Alto",
    "CRITICAL": "Crítico"
}


# ==========================================================
# Carregamento do dataset
# ==========================================================

@st.cache_data
def load_dataset(
    file_modified_time: float
) -> pd.DataFrame:
    """
    Carrega o dataset gerado pela aplicação.

    O parâmetro file_modified_time é utilizado para
    invalidar automaticamente o cache do Streamlit
    quando o dataset for gerado novamente pelo menu.
    """

    return pd.read_csv(
        DATASET_PATH
    )


# ==========================================================
# Avaliação determinística dos sensores
# ==========================================================

def calculate_sensor_risk(
    soil_moisture: float,
    pitch: float,
    roll: float,
    water_distance: float
) -> dict:
    """
    Reproduz no dashboard as mesmas regras determinísticas
    utilizadas na aplicação embarcada para avaliar:

    - umidade do solo;
    - pitch;
    - roll;
    - distância do corpo d'água.

    Essa função é utilizada pelo simulador manual.
    """

    # ------------------------------------------------------
    # Umidade do solo
    # ------------------------------------------------------

    if soil_moisture > 85:
        soil_risk = "CRITICAL"

    elif soil_moisture > 70:
        soil_risk = "HIGH"

    elif soil_moisture > 50:
        soil_risk = "MEDIUM"

    else:
        soil_risk = "LOW"


    # ------------------------------------------------------
    # Pitch
    # ------------------------------------------------------

    absolute_pitch = abs(
        pitch
    )

    if absolute_pitch > 15:
        pitch_risk = "CRITICAL"

    elif absolute_pitch > 10:
        pitch_risk = "HIGH"

    elif absolute_pitch > 5:
        pitch_risk = "MEDIUM"

    else:
        pitch_risk = "LOW"


    # ------------------------------------------------------
    # Roll
    # ------------------------------------------------------

    absolute_roll = abs(
        roll
    )

    if absolute_roll > 15:
        roll_risk = "CRITICAL"

    elif absolute_roll > 10:
        roll_risk = "HIGH"

    elif absolute_roll > 5:
        roll_risk = "MEDIUM"

    else:
        roll_risk = "LOW"


    # ------------------------------------------------------
    # Distância do corpo d'água
    # ------------------------------------------------------

    if water_distance < 20:
        water_risk = "CRITICAL"

    elif water_distance < 50:
        water_risk = "HIGH"

    elif water_distance <= 100:
        water_risk = "MEDIUM"

    else:
        water_risk = "LOW"


    # ------------------------------------------------------
    # Risco operacional dos sensores
    # ------------------------------------------------------

    risks = [
        soil_risk,
        pitch_risk,
        roll_risk,
        water_risk
    ]

    # Qualquer condição crítica.
    if "CRITICAL" in risks:

        sensor_operational_risk = (
            "CRITICAL"
        )

    # Inclinação elevada próxima do corpo d'água.
    elif (
        water_risk == "HIGH"
        and (
            pitch_risk == "HIGH"
            or roll_risk == "HIGH"
        )
    ):

        sensor_operational_risk = (
            "CRITICAL"
        )

    # Solo muito úmido combinado com inclinação elevada.
    elif (
        soil_risk == "HIGH"
        and (
            pitch_risk == "HIGH"
            or roll_risk == "HIGH"
        )
    ):

        sensor_operational_risk = (
            "CRITICAL"
        )

    # Duas ou mais condições altas.
    elif risks.count("HIGH") >= 2:

        sensor_operational_risk = (
            "CRITICAL"
        )

    # Duas ou mais condições médias.
    elif risks.count("MEDIUM") >= 2:

        sensor_operational_risk = (
            "HIGH"
        )

    # Uma condição alta.
    elif "HIGH" in risks:

        sensor_operational_risk = (
            "HIGH"
        )

    # Uma condição média.
    elif "MEDIUM" in risks:

        sensor_operational_risk = (
            "MEDIUM"
        )

    else:

        sensor_operational_risk = (
            "LOW"
        )


    return {
        "soil_risk": soil_risk,
        "pitch_risk": pitch_risk,
        "roll_risk": roll_risk,
        "water_risk": water_risk,
        "sensor_operational_risk":
            sensor_operational_risk
    }


# ==========================================================
# Cabeçalho
# ==========================================================

st.title(
    "🌱 AgroGuardian AI"
)

st.subheader(
    "Inteligência Preditiva para Risco Operacional "
    "de Máquinas Agrícolas"
)

st.markdown("---")


# ==========================================================
# Carregamento e processamento automático do dataset
# ==========================================================

st.subheader(
    "Análise dos Cenários Operacionais"
)


if not DATASET_PATH.exists():

    st.warning(
        "Dataset não encontrado. "
        "Gere o dataset pela opção "
        "'2 - Gerar Dataset' do menu antes "
        "de abrir o dashboard."
    )

    st.stop()


try:

    # ------------------------------------------------------
    # Controle de atualização do cache
    # ------------------------------------------------------

    file_modified_time = (
        DATASET_PATH
        .stat()
        .st_mtime
    )


    # ------------------------------------------------------
    # Carregamento do dataset
    # ------------------------------------------------------

    dataframe = load_dataset(
        file_modified_time
    )


    # ------------------------------------------------------
    # Previsões em lote
    # ------------------------------------------------------

    # O prediction_service aplica o pipeline treinado
    # aos registros e adiciona:
    #
    # - predicted_risk;
    # - predictive_risk_score;
    # - absolute_inclination.

    enriched_dataframe = (
        predict_dataframe(
            dataframe
        )
    )


except Exception as error:

    st.error(
        "Não foi possível carregar ou processar "
        "o dataset."
    )

    st.exception(
        error
    )

    st.stop()


# ==========================================================
# Métricas principais
# ==========================================================

total_records = len(
    enriched_dataframe
)

average_score = (
    enriched_dataframe[
        "predictive_risk_score"
    ]
    .mean()
)

high_critical_count = (
    enriched_dataframe[
        "predicted_risk"
    ]
    .isin(
        [
            "HIGH",
            "CRITICAL"
        ]
    )
    .sum()
)

high_critical_percentage = (
    high_critical_count
    / total_records
    * 100
)


# ----------------------------------------------------------
# Concordância ML x regras determinísticas
# ----------------------------------------------------------

if (
    "operational_risk"
    in enriched_dataframe.columns
):

    agreement_percentage = (
        (
            enriched_dataframe[
                "operational_risk"
            ]
            ==
            enriched_dataframe[
                "predicted_risk"
            ]
        )
        .mean()
        * 100
    )

else:

    agreement_percentage = None


col1, col2, col3, col4 = (
    st.columns(4)
)


with col1:

    st.metric(
        "Registros analisados",
        f"{total_records:,}"
    )


with col2:

    st.metric(
        "Score médio",
        f"{average_score:.2f}/100"
    )


with col3:

    st.metric(
        "Risco Alto/Crítico",
        f"{high_critical_percentage:.2f}%"
    )


with col4:

    if agreement_percentage is not None:

        st.metric(
            "Concordância ML x Regras",
            f"{agreement_percentage:.2f}%"
        )

    else:

        st.metric(
            "Concordância ML x Regras",
            "N/D"
        )


st.markdown("---")


# ==========================================================
# Gráfico 1
# Distribuição dos níveis de risco
# ==========================================================

st.subheader(
    "Distribuição dos Níveis de Risco"
)


risk_distribution = (
    enriched_dataframe[
        "predicted_risk"
    ]
    .value_counts()
    .reindex(
        RISK_ORDER,
        fill_value=0
    )
    .reset_index()
)


risk_distribution.columns = [
    "Risco",
    "Quantidade"
]


risk_distribution[
    "Risco"
] = risk_distribution[
    "Risco"
].map(
    RISK_LABELS
)


bar_chart = px.bar(
    risk_distribution,
    x="Risco",
    y="Quantidade",
    text="Quantidade",
    title=(
        "Distribuição das Classificações Previstas"
    ),
    labels={
        "Risco": "Nível de risco",
        "Quantidade": "Quantidade de cenários"
    }
)


st.plotly_chart(
    bar_chart,
    use_container_width=True
)


st.markdown("---")


# ==========================================================
# Gráfico 2
# Histograma do score preditivo
# ==========================================================

st.subheader(
    "Distribuição do Score Preditivo"
)


histogram = px.histogram(
    enriched_dataframe,
    x="predictive_risk_score",
    nbins=20,
    title=(
        "Distribuição dos Scores de Risco"
    ),
    labels={
        "predictive_risk_score":
            "Score preditivo"
    }
)


histogram.update_layout(
    xaxis_title="Score preditivo",
    yaxis_title="Quantidade de cenários"
)


st.plotly_chart(
    histogram,
    use_container_width=True
)


st.markdown("---")


# ==========================================================
# Gráfico 3
# Umidade do solo x inclinação absoluta
# ==========================================================

st.subheader(
    "Umidade do Solo x Inclinação"
)


# absolute_inclination representa a maior magnitude
# encontrada entre Pitch e Roll.
#
# Pitch e Roll continuam separados no modelo e nas regras.
# Essa variável existe somente para facilitar a análise
# visual no dashboard.

scatter = px.scatter(
    enriched_dataframe,
    x="soil_moisture",
    y="absolute_inclination",
    color="predicted_risk",
    hover_data=[
        "pitch",
        "roll",
        "water_distance",
        "precipitation_mm",
        "predictive_risk_score"
    ],
    title=(
        "Relação entre Umidade e "
        "Inclinação Operacional"
    ),
    labels={
        "soil_moisture":
            "Umidade do solo (%)",
        "absolute_inclination":
            "Maior inclinação absoluta (°)",
        "predicted_risk":
            "Risco previsto",
        "pitch":
            "Pitch (°)",
        "roll":
            "Roll (°)",
        "water_distance":
            "Distância da água (m)",
        "precipitation_mm":
            "Precipitação (mm)",
        "predictive_risk_score":
            "Score preditivo"
    }
)


st.plotly_chart(
    scatter,
    use_container_width=True
)


st.markdown("---")


# ==========================================================
# Gráfico 4
# Heatmap de correlação
# ==========================================================

st.subheader(
    "Correlação das Variáveis"
)


correlation_columns = [
    "soil_moisture",
    "pitch",
    "roll",
    "water_distance",
    "precipitation_mm",
    "absolute_inclination",
    "predictive_risk_score"
]


correlation_matrix = (
    enriched_dataframe[
        correlation_columns
    ]
    .corr()
)


correlation_labels = {
    "soil_moisture":
        "Umidade",
    "pitch":
        "Pitch",
    "roll":
        "Roll",
    "water_distance":
        "Distância Água",
    "precipitation_mm":
        "Precipitação",
    "absolute_inclination":
        "Inclinação",
    "predictive_risk_score":
        "Score"
}


correlation_matrix = (
    correlation_matrix.rename(
        index=correlation_labels,
        columns=correlation_labels
    )
)


heatmap = px.imshow(
    correlation_matrix,
    text_auto=".2f",
    aspect="auto",
    title=(
        "Mapa de Correlação das "
        "Variáveis Operacionais"
    )
)


st.plotly_chart(
    heatmap,
    use_container_width=True
)


st.markdown("---")


# ==========================================================
# Visualização dos dados processados
# ==========================================================

with st.expander(
    "Visualizar dados processados"
):

    st.dataframe(
        enriched_dataframe,
        use_container_width=True
    )


# ==========================================================
# Simulador de cenário
# ==========================================================

st.markdown("---")

st.subheader(
    "Simulador de Cenário"
)

st.write(
    "Informe as condições operacionais para analisar "
    "o risco pelas regras determinísticas e realizar "
    "uma previsão utilizando o modelo de Machine Learning."
)


# ==========================================================
# Entradas do simulador
# ==========================================================

col1, col2, col3 = (
    st.columns(3)
)


with col1:

    soil_moisture = st.slider(
        "Umidade do Solo (%)",
        min_value=0.0,
        max_value=100.0,
        value=50.0,
        step=1.0
    )


with col2:

    pitch = st.slider(
        "Pitch (°)",
        min_value=-40.0,
        max_value=40.0,
        value=0.0,
        step=1.0
    )


with col3:

    roll = st.slider(
        "Roll (°)",
        min_value=-40.0,
        max_value=40.0,
        value=0.0,
        step=1.0
    )


col4, col5 = (
    st.columns(2)
)


with col4:

    water_distance = st.slider(
        "Distância do Corpo d'Água (m)",
        min_value=0.0,
        max_value=1000.0,
        value=300.0,
        step=10.0
    )


with col5:

    precipitation_mm = st.slider(
        "Precipitação Acumulada (mm)",
        min_value=0.0,
        max_value=60.0,
        value=20.0,
        step=1.0
    )


# ==========================================================
# Análise do cenário
# ==========================================================

if st.button(
    "Analisar Risco"
):

    # ------------------------------------------------------
    # Riscos provenientes dos sensores
    # ------------------------------------------------------

    sensor_risks = (
        calculate_sensor_risk(
            soil_moisture=
                soil_moisture,
            pitch=
                pitch,
            roll=
                roll,
            water_distance=
                water_distance
        )
    )


    # ------------------------------------------------------
    # Risco da precipitação
    # ------------------------------------------------------

    precipitation_risk = (
        evaluate_precipitation_risk(
            precipitation_mm
        )
    )


    # ------------------------------------------------------
    # Risco operacional determinístico
    # ------------------------------------------------------

    operational_risk = (
        evaluate_operational_risk(
            sensor_operational_risk=
                sensor_risks[
                    "sensor_operational_risk"
                ],
            precipitation_risk=
                precipitation_risk,
            soil_risk=
                sensor_risks[
                    "soil_risk"
                ],
            pitch_risk=
                sensor_risks[
                    "pitch_risk"
                ],
            roll_risk=
                sensor_risks[
                    "roll_risk"
                ],
            water_risk=
                sensor_risks[
                    "water_risk"
                ]
        )
    )


    # ------------------------------------------------------
    # Cenário utilizado pelo modelo preditivo
    # ------------------------------------------------------

    scenario = {
        "soil_moisture":
            soil_moisture,
        "pitch":
            pitch,
        "roll":
            roll,
        "water_distance":
            water_distance,
        "precipitation_mm":
            precipitation_mm
    }


    # ------------------------------------------------------
    # Previsão Machine Learning
    # ------------------------------------------------------

    prediction = (
        get_prediction(
            scenario
        )
    )


    predicted_risk = (
        prediction[
            "predicted_risk"
        ]
    )


    predictive_score = (
        prediction[
            "predictive_risk_score"
        ]
    )


    probabilities = (
        prediction[
            "risk_probabilities"
        ]
    )


    # ======================================================
    # Resultado da análise
    # ======================================================

    st.markdown("---")

    st.subheader(
        "Resultado da Análise"
    )


    result_col1, result_col2, result_col3 = (
        st.columns(3)
    )


    with result_col1:

        st.metric(
            "Risco pelas Regras",
            RISK_LABELS.get(
                operational_risk,
                operational_risk
            )
        )


    with result_col2:

        st.metric(
            "Risco Previsto pelo ML",
            RISK_LABELS.get(
                predicted_risk,
                predicted_risk
            )
        )


    with result_col3:

        st.metric(
            "Score Preditivo",
            f"{predictive_score:.2f}/100"
        )


    # ======================================================
    # Avaliação dos fatores
    # ======================================================

    st.write(
        "### Avaliação dos Fatores"
    )


    factor_dataframe = pd.DataFrame({
        "Fator": [
            "Umidade do solo",
            "Pitch",
            "Roll",
            "Corpo d'água",
            "Precipitação"
        ],

        "Risco": [
            RISK_LABELS.get(
                sensor_risks[
                    "soil_risk"
                ]
            ),

            RISK_LABELS.get(
                sensor_risks[
                    "pitch_risk"
                ]
            ),

            RISK_LABELS.get(
                sensor_risks[
                    "roll_risk"
                ]
            ),

            RISK_LABELS.get(
                sensor_risks[
                    "water_risk"
                ]
            ),

            RISK_LABELS.get(
                precipitation_risk
            )
        ]
    })


    st.dataframe(
        factor_dataframe,
        use_container_width=True,
        hide_index=True
    )


    # ======================================================
    # Probabilidades do modelo
    # ======================================================

    st.write(
        "### Probabilidades do Modelo"
    )


    probabilities_dataframe = (
        pd.DataFrame({
            "Risco": [
                RISK_LABELS[
                    risk
                ]
                for risk
                in RISK_ORDER
            ],

            "Probabilidade": [
                (
                    probabilities.get(
                        risk,
                        0.0
                    )
                    * 100
                )
                for risk
                in RISK_ORDER
            ]
        })
    )


    probability_chart = px.bar(
        probabilities_dataframe,
        x="Risco",
        y="Probabilidade",
        text_auto=".1f",
        title=(
            "Probabilidade por Nível "
            "de Risco"
        ),
        labels={
            "Risco":
                "Nível de risco",
            "Probabilidade":
                "Probabilidade (%)"
        }
    )


    st.plotly_chart(
        probability_chart,
        use_container_width=True
    )


# ==========================================================
# Rodapé
# ==========================================================

st.markdown("---")

st.caption(
    "AgroGuardian AI • "
    "Análise de Risco Operacional "
    "para Máquinas Agrícolas"
)