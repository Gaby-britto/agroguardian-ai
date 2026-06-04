import streamlit as st
import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier

# ==========================================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="AgroGuardian AI",
    page_icon="🌱",
    layout="wide"
)

# ==========================================================
# CARREGA DADOS DO BANCO
# ==========================================================

@st.cache_data
def carregar_dados():
    conn = sqlite3.connect("database/agroguardian.db")

    df = pd.read_sql(
        "SELECT * FROM sensors",
        conn
    )

    conn.close()

    return df


df = carregar_dados()

# ==========================================================
# TREINA MODELO
# ==========================================================

X = df[
    [
        "umidade",
        "inclinacao",
        "distancia_agua",
        "chuva",
        "historico"
    ]
]

y = df["risco"]

modelo = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

modelo.fit(X, y)

# ==========================================================
# TÍTULO
# ==========================================================

st.title("🌱 AgroGuardian AI")
st.subheader(
    "Inteligência Preditiva para Operações Agrícolas"
)

st.markdown("---")

# ==========================================================
# MÉTRICAS
# ==========================================================

risco_predominante = (
    df["risco"]
    .value_counts()
    .idxmax()
)

total_registros = len(df)

col1, col2 = st.columns(2)

with col1:
    st.metric(
        " Registros Monitorados",
        total_registros
    )

with col2:
    st.metric(
        " Risco Predominante",
        risco_predominante
    )

st.markdown("---")

# ==========================================================
# DISTRIBUIÇÃO DOS RISCOS
# ==========================================================

st.subheader("Distribuição dos Níveis de Risco")

risco_count = (
    df["risco"]
    .value_counts()
)

st.bar_chart(risco_count)

st.markdown("---")

# ==========================================================
# IMPORTÂNCIA DAS VARIÁVEIS
# ==========================================================

st.subheader(" Importância das Variáveis")

importancia = pd.DataFrame({
    "Variável": X.columns,
    "Importância": modelo.feature_importances_
})

importancia = importancia.sort_values(
    by="Importância",
    ascending=False
)

st.dataframe(
    importancia,
    use_container_width=True
)

st.markdown("---")

# ==========================================================
# TABELA DE DADOS
# ==========================================================

st.subheader(" Dados Monitorados")

st.dataframe(
    df,
    use_container_width=True
)

st.markdown("---")

# ==========================================================
# SIMULADOR DE RISCO
# ==========================================================

st.subheader(" Simulador de Cenário")

col1, col2 = st.columns(2)

with col1:

    umidade = st.slider(
        "Umidade do Solo (%)",
        0,
        100,
        50
    )

    inclinacao = st.slider(
        "Inclinação do Terreno (°)",
        0,
        35,
        10
    )

    distancia_agua = st.slider(
        "Distância da Água (m)",
        0,
        1000,
        300
    )

with col2:

    chuva = st.slider(
        "Chuva Acumulada (mm)",
        0,
        60,
        20
    )

    historico = st.slider(
        "Histórico de Incidentes",
        0,
        5,
        1
    )

# ==========================================================
# BOTÃO DE PREVISÃO
# ==========================================================

if st.button(" Analisar Risco"):

    novo_cenario = pd.DataFrame({
        "umidade": [umidade],
        "inclinacao": [inclinacao],
        "distancia_agua": [distancia_agua],
        "chuva": [chuva],
        "historico": [historico]
    })

    risco_previsto = modelo.predict(
        novo_cenario
    )[0]

    st.markdown("---")

    st.subheader("Resultado da Análise")

    if risco_previsto == "Baixo":

        st.success(" RISCO BAIXO")

        st.info("""
        Recomendação:
        • Operação liberada.
        • Condições consideradas seguras.
        • Continuar monitoramento preventivo.
        """)

    elif risco_previsto == "Medio":

        st.warning(" RISCO MÉDIO")

        st.info("""
        Recomendação:
        • Monitorar condições climáticas.
        • Reduzir velocidade da operação.
        • Avaliar o terreno antes da execução.
        """)

    elif risco_previsto == "Alto":

        st.error(" RISCO ALTO")

        st.info("""
        Recomendação:
        • Avaliar necessidade da operação.
        • Evitar áreas próximas a corpos d'água.
        • Realizar inspeção preventiva dos equipamentos.
        """)

    else:

        st.error(" RISCO CRÍTICO")

        st.info("""
        Recomendação:
        • Operação não recomendada.
        • Aguardar melhoria das condições do solo.
        • Redefinir rota ou cronograma da atividade.
        """)

    st.write(
        f"### Classificação Prevista: **{risco_previsto}**"
    )

# ==========================================================
# RODAPÉ
# ==========================================================

st.markdown("---")

st.caption(
    "AgroGuardian AI • Challenge Sompo Seguros • FIAP"
)