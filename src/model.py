import os

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)
from sklearn.model_selection import (
    train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


# ==========================================================
# Configurações
# ==========================================================

DATASET_PATH = (
    "data/dataset_agroguardian.csv"
)

MODEL_DIRECTORY = "models"

MODEL_PATH = (
    f"{MODEL_DIRECTORY}/"
    "operational_risk_model.joblib"
)

RANDOM_STATE = 42

TEST_SIZE = 0.20


# ==========================================================
# Variáveis utilizadas pelo modelo
# ==========================================================

# O modelo utiliza somente os dados primários disponíveis
# durante uma operação real.
#
# Os campos de risco calculados pelas regras determinísticas
# não são utilizados como features, evitando vazamento de
# informação durante o treinamento.

FEATURES = [
    "soil_moisture",
    "pitch",
    "roll",
    "water_distance",
    "precipitation_mm"
]

TARGET = "operational_risk"


# ==========================================================
# Carregamento do dataset
# ==========================================================

print(
    "\nCarregando dataset..."
)

df = pd.read_csv(
    DATASET_PATH
)

print(
    "Dataset carregado com sucesso!"
)

print(
    f"Total de registros: {len(df)}"
)


# ==========================================================
# Preparação das variáveis
# ==========================================================

X = df[
    FEATURES
].copy()

y = df[
    TARGET
].copy()


print(
    "\nFeatures utilizadas:"
)

for feature in FEATURES:
    print(
        f"- {feature}"
    )

print(
    f"\nVariável alvo: {TARGET}"
)


# ==========================================================
# Distribuição da variável alvo
# ==========================================================

print(
    "\nDistribuição das classes:"
)

print(
    y.value_counts()
)

print(
    "\nDistribuição percentual:"
)

print(
    (
        y.value_counts(
            normalize=True
        )
        * 100
    ).round(2)
)


# ==========================================================
# Separação entre treino e teste
# ==========================================================

# stratify mantém aproximadamente a mesma proporção
# das classes nos conjuntos de treino e teste.

X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y
    )
)


print(
    "\nDados separados para treino e teste."
)

print(
    f"Treinamento: {len(X_train)} registros"
)

print(
    f"Teste: {len(X_test)} registros"
)


# ==========================================================
# Pipeline de pré-processamento numérico
# ==========================================================

# Todas as features utilizadas atualmente são numéricas.
#
# O pipeline executa:
#
# 1. tratamento de valores ausentes utilizando a mediana;
# 2. padronização das variáveis numéricas.
#
# A utilização do pipeline garante que exatamente as mesmas
# transformações aplicadas durante o treinamento também
# sejam utilizadas posteriormente nas previsões.

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


# ==========================================================
# Pré-processador
# ==========================================================

# O ColumnTransformer permite definir quais transformações
# serão aplicadas a cada grupo de variáveis.
#
# Embora atualmente todas as features sejam numéricas,
# essa estrutura deixa o projeto preparado para receber
# variáveis categóricas futuramente sem alterar toda a
# arquitetura do treinamento.

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            FEATURES
        )
    ],
    remainder="drop"
)


# ==========================================================
# Modelo de Machine Learning
# ==========================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# ==========================================================
# Pipeline completo de Machine Learning
# ==========================================================

# O pipeline final encapsula:
#
# dados de entrada
#       ↓
# tratamento de valores ausentes
#       ↓
# padronização
#       ↓
# Random Forest
#
# Isso evita executar manualmente transformações diferentes
# durante treinamento e previsão.

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "classifier",
            model
        )
    ]
)


# ==========================================================
# Treinamento
# ==========================================================

print(
    "\nTreinando modelo..."
)

pipeline.fit(
    X_train,
    y_train
)

print(
    "Modelo treinado com sucesso!"
)


# ==========================================================
# Previsões
# ==========================================================

predictions = pipeline.predict(
    X_test
)

print(
    "\nPrevisões realizadas com sucesso!"
)


# ==========================================================
# Accuracy
# ==========================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    "\n"
    + "=" * 50
)

print(
    "MÉTRICAS DO MODELO"
)

print(
    "=" * 50
)

print(
    "\nAccuracy:"
)

print(
    f"{accuracy:.2%}"
)


# ==========================================================
# Matriz de confusão
# ==========================================================

RISK_ORDER = [
    "LOW",
    "MEDIUM",
    "HIGH",
    "CRITICAL"
]

confusion = confusion_matrix(
    y_test,
    predictions,
    labels=RISK_ORDER
)

confusion_df = pd.DataFrame(
    confusion,
    index=[
        f"Real_{risk}"
        for risk in RISK_ORDER
    ],
    columns=[
        f"Pred_{risk}"
        for risk in RISK_ORDER
    ]
)


print(
    "\nMatriz de Confusão:"
)

print(
    confusion_df
)


# ==========================================================
# Relatório de classificação
# ==========================================================

print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        predictions,
        labels=RISK_ORDER,
        digits=4
    )
)


# ==========================================================
# Importância das variáveis
# ==========================================================

# Após o treinamento, acessamos o Random Forest que está
# armazenado dentro do pipeline.

trained_model = (
    pipeline.named_steps[
        "classifier"
    ]
)

feature_importance = pd.DataFrame({
    "feature": FEATURES,
    "importance":
        trained_model.feature_importances_
})

feature_importance = (
    feature_importance
    .sort_values(
        by="importance",
        ascending=False
    )
    .reset_index(
        drop=True
    )
)


print(
    "\nImportância das Variáveis:"
)

print(
    feature_importance
)


# ==========================================================
# Persistência do modelo
# ==========================================================

# Salvamos o pipeline completo e não apenas o
# RandomForestClassifier.
#
# Dessa forma, o arquivo contém tanto o pré-processamento
# quanto o modelo treinado.

os.makedirs(
    MODEL_DIRECTORY,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_PATH
)

print(
    "\nModelo salvo com sucesso!"
)

print(
    f"Arquivo: {MODEL_PATH}"
)


# ==========================================================
# Exemplo de previsão
# ==========================================================

# Simula uma nova leitura utilizando exatamente as mesmas
# cinco variáveis que estarão disponíveis na aplicação.

new_scenario = pd.DataFrame({
    "soil_moisture": [65.0],
    "pitch": [8.0],
    "roll": [3.0],
    "water_distance": [180.0],
    "precipitation_mm": [20.0]
})


predicted_risk = pipeline.predict(
    new_scenario
)[0]


print(
    "\n"
    + "=" * 50
)

print(
    "EXEMPLO DE PREVISÃO"
)

print(
    "=" * 50
)

print(
    "\nCenário:"
)

print(
    new_scenario.to_string(
        index=False
    )
)

print(
    "\nRisco previsto:"
)

print(
    predicted_risk
)


# ==========================================================
# Finalização
# ==========================================================

print(
    "\nTreinamento finalizado com sucesso!"
)