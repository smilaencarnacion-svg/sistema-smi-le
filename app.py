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

# ---------------- EDITAR ----------------
@app.route('/editar/<int:id>', methods=['POST'])
def editar(id):
    conn = conectar()
    conn.execute("""
    UPDATE pacientes SET 
    expediente=?,p1=?,p2=?,a1=?,a2=?,identidad=?,fecha=?,sexo=?,departamento=?,municipio=?,aldea=?
    WHERE id=?
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
        request.form.get('aldea',''),
        id
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

# ---------------- IMPORTAR EXCEL (ARREGLADO) ----------------
@app.route('/importar', methods=['POST'])
def importar():
    if 'archivo' not in request.files:
        return redirect('/panel')

    archivo = request.files['archivo']

    if archivo.filename == '':
        return redirect('/panel')

    try:
        df = pd.read_excel(archivo, engine='openpyxl')
    except:
        return redirect('/panel')

    conn = conectar()

    for _, row in df.iterrows():
        try:
            fila = []
            for i in range(11):
                valor = row[i] if i < len(row) else ""
                if pd.isna(valor):
                    valor = ""
                fila.append(str(valor))

            conn.execute("""
            INSERT INTO pacientes 
            (expediente,p1,p2,a1,a2,identidad,fecha,sexo,departamento,municipio,aldea)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(fila))
        except:
            continue

    conn.commit()
    conn.close()

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