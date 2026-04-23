import sqlite3

conexion = sqlite3.connect("expedientes.db")
cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_expediente TEXT,
    nombre_completo TEXT,
    identidad TEXT,
    fecha_nacimiento TEXT,
    edad INTEGER,
    sexo TEXT,
    direccion TEXT
)
""")

conexion.commit()
conexion.close()

print("Base de datos creada")