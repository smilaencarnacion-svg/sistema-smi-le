from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import sqlite3

app = Flask(__name__)
app.secret_key = "clave123"

# ---------------- DB ----------------
def conectar():
    return sqlite3.connect("database.db")

def crear_tabla():
    conn = conectar()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expediente TEXT,
        p1 TEXT,
        p2 TEXT,
        a1 TEXT,
        a2 TEXT,
        identidad TEXT,
        fecha TEXT,
        sexo TEXT,
        departamento TEXT,
        municipio TEXT,
        aldea TEXT
    )
    """)
    conn.commit()
    conn.close()

crear_tabla()

# ---------------- LOGIN ----------------
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    if request.form['usuario']=="SMI-LE" and request.form['clave']=="SMI-LE26":
        session['user']=True
        return redirect('/panel')
    return render_template('login.html', error="Credenciales incorrectas")

# ---------------- PANEL ----------------
@app.route('/panel')
def panel():
    if 'user' not in session:
        return redirect('/')

    conn = conectar()
    datos = conn.execute("SELECT * FROM pacientes").fetchall()
    conn.close()

    return render_template('dashboard.html', data=datos)

# ---------------- AGREGAR ----------------
@app.route('/agregar', methods=['POST'])
def agregar():
    conn = conectar()
    conn.execute("""
    INSERT INTO pacientes 
    (expediente,p1,p2,a1,a2,identidad,fecha,sexo,departamento,municipio,aldea)
    VALUES (?,?,?,?,?,?,?,?,?,?,?)
    """, (
        request.form.get('expediente',''),
        request.form.get('p1',''),
        request.form.get('p2',''),
        request.form.get('a1',''),
        request.form.get('a2',''),
        request.form.get('identidad',''),
        request.form.get('fecha',''),
        request.form.get('sexo',''),
        request.form.get('departamento',''),
        request.form.get('municipio',''),
        request.form.get('aldea','')
    ))
    conn.commit()
    conn.close()
    return redirect('/panel')

# ---------------- ELIMINAR ----------------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = conectar()
    conn.execute("DELETE FROM pacientes WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/panel')

# ---------------- ELIMINAR TODO ----------------
@app.route('/eliminar_todo')
def eliminar_todo():
    conn = conectar()
    conn.execute("DELETE FROM pacientes")
    conn.commit()
    conn.close()
    return redirect('/panel')

# ---------------- IMPORTAR EXCEL (SOLUCIÓN REAL) ----------------
@app.route('/importar', methods=['POST'])
def importar():
    archivo = request.files.get('archivo')

    if not archivo or archivo.filename == "":
        print("❌ No se seleccionó archivo")
        return redirect('/panel')

    try:
        # Lee TODO como texto para evitar errores
        df = pd.read_excel(archivo, engine='openpyxl', dtype=str)
    except Exception as e:
        print("❌ Error leyendo Excel:", e)
        return redirect('/panel')

    conn = conectar()

    for _, row in df.iterrows():
        try:
            # Convierte fila completa a lista segura
            datos = list(row.values)

            # Asegura 11 columnas exactas
            while len(datos) < 11:
                datos.append("")

            datos = datos[:11]

            # Limpia valores nulos
            datos = [("" if str(x) == "nan" else str(x)) for x in datos]

            conn.execute("""
            INSERT INTO pacientes 
            (expediente,p1,p2,a1,a2,identidad,fecha,sexo,departamento,municipio,aldea)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(datos))

        except Exception as e:
            print("⚠️ Fila ignorada:", e)
            continue

    conn.commit()
    conn.close()

    print("✅ Excel importado correctamente")
    return redirect('/panel')

# ---------------- EXPORTAR EXCEL ----------------
@app.route('/exportar')
def exportar():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM pacientes", conn)
    conn.close()

    archivo = "datos.xlsx"
    df.to_excel(archivo, index=False)

    return send_file(archivo, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)