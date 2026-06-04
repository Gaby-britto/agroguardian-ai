import sqlite3
import pandas as pd
import os
from datetime import datetime

# ==========================================================
# AgroGuardian AI - Database Setup
# Challenge Sompo Seguros
# Sprint 2 - Engenharia de Dados
# ==========================================================

# Cria a pasta database caso não exista
os.makedirs("database", exist_ok=True)

# Caminhos dos arquivos
DATABASE_PATH = "database/agroguardian.db"
DATASET_PATH = "data/dataset_sompo.csv"

# ==========================================================
# Conexão com banco
# ==========================================================

print("🔌 Conectando ao banco...")

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

print(" Banco conectado com sucesso!")

# ==========================================================
# Criação da tabela
# ==========================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    umidade REAL,
    inclinacao REAL,
    distancia_agua REAL,
    chuva REAL,
    solo TEXT,
    operacao TEXT,
    historico INTEGER,
    risco TEXT,
    data_registro TIMESTAMP
)
""")

print(" Tabela criada/verificada!")

# ==========================================================
# Leitura do dataset
# ==========================================================

df = pd.read_csv(DATASET_PATH)

print(f" Dataset carregado: {len(df)} registros")

# Adiciona timestamp de inserção
df["data_registro"] = datetime.now()

# ==========================================================
# Inserção dos dados
# ==========================================================

df.to_sql(
    "sensors",
    conn,
    if_exists="append",
    index=False
)

print(" Dados inseridos com sucesso!")

# ==========================================================
# Consulta de validação
# ==========================================================

print("\n Primeiros registros:")

query = """
SELECT *
FROM sensors
LIMIT 5
"""

result = pd.read_sql(query, conn)

print(result)

# ==========================================================
# Estatísticas de risco
# ==========================================================

print("\n Distribuição dos riscos:")

query_risk = """
SELECT
    risco,
    COUNT(*) AS quantidade
FROM sensors
GROUP BY risco
ORDER BY quantidade DESC
"""

risk_stats = pd.read_sql(query_risk, conn)

print(risk_stats)

# ==========================================================
# Total de registros
# ==========================================================

query_total = """
SELECT COUNT(*) AS total_registros
FROM sensors
"""

total = pd.read_sql(query_total, conn)

print("\n Total armazenado no banco:")
print(total)

# ==========================================================
# Finalização
# ==========================================================

conn.commit()
conn.close()

print(f"\n Banco salvo em: {DATABASE_PATH}")
print(" Processo finalizado com sucesso!")