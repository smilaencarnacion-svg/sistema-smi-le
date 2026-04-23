from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)
app.secret_key = "clave_segura_123"

# -------- DB --------
def conectar():
    return sqlite3.connect("database.db")

def crear_tabla():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expediente TEXT,
        primer_nombre TEXT,
        segundo_nombre TEXT,
        primer_apellido TEXT,
        segundo_apellido TEXT,
        identidad TEXT,
        fecha_nacimiento TEXT,
        sexo TEXT,
        departamento TEXT,
        municipio TEXT,
        aldea TEXT
    )
    """)
    conn.commit()
    conn.close()

crear_tabla()

# -------- LOGIN --------
@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form.get('usuario')
    clave = request.form.get('clave')

    if usuario == "admin" and clave == "1234":
        session['user'] = usuario
        return redirect('/panel')

    return "Credenciales incorrectas"

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------- PANEL --------
@app.route('/panel')
def panel():
    if 'user' not in session:
        return redirect('/')

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    datos = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', datos=datos)

# -------- GUARDAR --------
@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.json

    conn = conectar()
    cursor = conn.cursor()

    if data.get("id"):
        cursor.execute("""
        UPDATE pacientes SET
            expediente=?, primer_nombre=?, segundo_nombre=?,
            primer_apellido=?, segundo_apellido=?, identidad=?,
            fecha_nacimiento=?, sexo=?, departamento=?,
            municipio=?, aldea=?
        WHERE id=?
        """, (
            data["expediente"], data["primer_nombre"], data["segundo_nombre"],
            data["primer_apellido"], data["segundo_apellido"], data["identidad"],
            data["fecha_nacimiento"], data["sexo"], data["departamento"],
            data["municipio"], data["aldea"], data["id"]
        ))
    else:
        cursor.execute("""
        INSERT INTO pacientes (
            expediente, primer_nombre, segundo_nombre,
            primer_apellido, segundo_apellido,
            identidad, fecha_nacimiento, sexo,
            departamento, municipio, aldea
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["expediente"], data["primer_nombre"], data["segundo_nombre"],
            data["primer_apellido"], data["segundo_apellido"], data["identidad"],
            data["fecha_nacimiento"], data["sexo"], data["departamento"],
            data["municipio"], data["aldea"]
        ))

    conn.commit()
    conn.close()
    return jsonify({"ok": True})

# -------- ELIMINAR --------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pacientes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/panel')

# -------- IMPORTAR EXCEL --------
@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files['archivo']
    df = pd.read_excel(archivo)

    conn = conectar()
    cursor = conn.cursor()

    for _, fila in df.iterrows():
        cursor.execute("""
        INSERT INTO pacientes (
            expediente, primer_nombre, segundo_nombre,
            primer_apellido, segundo_apellido,
            identidad, fecha_nacimiento, sexo,
            departamento, municipio, aldea
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, tuple(fila))

    conn.commit()
    conn.close()
    return redirect('/panel')

if __name__ == "__main__":
    app.run(debug=True)