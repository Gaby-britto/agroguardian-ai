# Importa bibliotecas necessárias
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import confusion_matrix, classification_report

import sqlite3

conn = sqlite3.connect("agroguardian.db")

# Lê dados da tabela sensors
df = pd.read_sql("SELECT * FROM sensors", conn)

conn.close()

print("✅ Data loaded from database!")


# Variáveis de entrada (features)
X = df[['umidade', 'inclinacao', 'distancia_agua', 'chuva', 'historico']]

# Variável alvo (target)
y = df['risco']


# ==========================================
# 3. SEPARAR TREINO E TESTE
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("✅ Data split into train and test!")


# ==========================================
# 4. CRIAR E TREINAR MODELO
# ==========================================

model = DecisionTreeClassifier()

model.fit(X_train, y_train)

print("✅ Model trained!")


# ==========================================
# 5. FAZER PREVISÕES
# ==========================================

predictions = model.predict(X_test)

print("✅ Predictions generated!")


# ==========================================
# 6. VALIDAR MODELO
# ==========================================

print("\n📊 Confusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\n📊 Classification Report:")
print(classification_report(y_test, predictions))
