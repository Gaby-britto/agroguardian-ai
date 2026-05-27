import sqlite3

import pandas as pd


# Cria o banco
conn = sqlite3.connect("agroguardian.db")

# Cria cursor para rodar comandos SQL
cursor = conn.cursor()

print("✅ Database connected successfully!")


# Lê o dataset CSV gerado anteriormente
df = pd.read_csv("dataset_sompo.csv")

print("✅ Dataset loaded!")


cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    umidity REAL,
    inclination REAL,
    distance_from_water REAL,
    rainfall REAL,
    soil TEXT,
    operation TEXT,
    history INTEGER,
    risk INTEGER
)
""")

print("✅ Table created!")


# Usa pandas para enviar os dados automaticamente
df.to_sql("sensors", conn, if_exists="replace", index=False)

print("✅ Data inserted into database!")


query = "SELECT * FROM sensors LIMIT 5"

result = pd.read_sql(query, conn)

print("\n Sample data from database:")
print(result)


conn.close()

print("\n✅ Database connection closed!")