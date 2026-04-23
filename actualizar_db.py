import sqlite3

conn = sqlite3.connect('expedientes.db')
cursor = conn.cursor()

columnas = [
    "numero_expediente",
    "primer_nombre",
    "segundo_nombre",
    "primer_apellido",
    "segundo_apellido",
    "identidad",
    "fecha_nacimiento",
    "sexo",
    "departamento",
    "municipio",
    "aldea_caserio"
]

for col in columnas:
    try:
        cursor.execute(f"ALTER TABLE expedientes ADD COLUMN {col} TEXT")
    except:
        pass

conn.commit()
conn.close()

print("BASE DE DATOS LISTA")