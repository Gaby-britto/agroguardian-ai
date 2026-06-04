import sqlite3
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    accuracy_score
)

# ==========================================================
# 1. CONECTA AO BANCO
# ==========================================================

print("Conectando ao banco...")

conn = sqlite3.connect("database/agroguardian.db")

df = pd.read_sql(
    "SELECT * FROM sensors",
    conn
)

conn.close()

print("Dados carregados com sucesso!")
print(f"Total de registros: {len(df)}")

# ==========================================================
# 2. PREPARAÇÃO DOS DADOS
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

# ==========================================================
# 3. CORRELAÇÃO
# ==========================================================

print("\nCorrelação das variáveis:")

correlation = X.corr()

print(correlation)

# ==========================================================
# 4. TREINO E TESTE
# ==========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nDados separados para treino e teste.")

# ==========================================================
# 5. TREINAMENTO
# ==========================================================

model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

print("Modelo treinado com sucesso!")

# ==========================================================
# 6. PREVISÕES
# ==========================================================

predictions = model.predict(X_test)

print("Previsões realizadas!")

# ==========================================================
# 7. MÉTRICAS
# ==========================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

print("\nACCURACY:")
print(f"{accuracy:.2%}")

print("\nMATRIZ DE CONFUSÃO:")
print(
    confusion_matrix(
        y_test,
        predictions
    )
)

print("\nCLASSIFICATION REPORT:")
print(
    classification_report(
        y_test,
        predictions
    )
)

# ==========================================================
# 8. IMPORTÂNCIA DAS VARIÁVEIS
# ==========================================================

print("\nImportância das variáveis:")

importance = pd.DataFrame({
    "Variavel": X.columns,
    "Importancia": model.feature_importances_
})

importance = importance.sort_values(
    by="Importancia",
    ascending=False
)

print(importance)

# ==========================================================
# 9. EXEMPLO DE PREVISÃO
# ==========================================================

novo_cenario = pd.DataFrame({
    "umidade": [88],
    "inclinacao": [22],
    "distancia_agua": [45],
    "chuva": [40],
    "historico": [3]
})

risco_previsto = model.predict(
    novo_cenario
)

print("\nExemplo de previsão:")

print(
    f"Risco previsto: {risco_previsto[0]}"
)

# ==========================================================
# FIM
# ==========================================================